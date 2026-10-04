"""Tests for deterministic pollution analytics engine (Lab 2)."""

import pandas as pd
import pytest
from clean_air_agent.tools.analytics import (
    calculate_statistics,
    find_peak_pollution,
    compare_stations,
    detect_missing_data,
    detect_significant_changes,
    analyze_air_quality,
)

SAMPLE_OBSERVATIONS = [
    {"station": "Anand Vihar", "timestamp": "2026-09-19 10:00", "pm25": 100.0, "pm10": 180.0, "latitude": 28.65, "longitude": 77.31},
    {"station": "Anand Vihar", "timestamp": "2026-09-19 11:00", "pm25": 150.0, "pm10": 240.0, "latitude": 28.65, "longitude": 77.31},
    {"station": "Anand Vihar", "timestamp": "2026-09-19 12:00", "pm25": 200.0, "pm10": 300.0, "latitude": 28.65, "longitude": 77.31},
    {"station": "Pusa", "timestamp": "2026-09-19 10:00", "pm25": 50.0, "pm10": 90.0, "latitude": 28.63, "longitude": 77.15},
    {"station": "Pusa", "timestamp": "2026-09-19 11:00", "pm25": 60.0, "pm10": 110.0, "latitude": 28.63, "longitude": 77.15},
    {"station": "Pusa", "timestamp": "2026-09-19 12:00", "pm25": 70.0, "pm10": 120.0, "latitude": 28.63, "longitude": 77.15},
]


def test_calculate_statistics_pm25():
    """Verify deterministic statistics calculation for PM2.5."""
    stats = calculate_statistics(SAMPLE_OBSERVATIONS, parameter="pm25")

    assert stats["min"] == 50.0
    assert stats["max"] == 200.0
    assert stats["mean"] == pytest.approx(105.0, 0.1)
    assert stats["median"] == pytest.approx(85.0, 0.1)
    assert stats["latest"] == 70.0
    assert stats["count"] == 6
    assert stats["time_of_max"] == "2026-09-19 12:00"


def test_find_peak_pollution():
    """Verify peak pollution station and value identification."""
    peak = find_peak_pollution(SAMPLE_OBSERVATIONS, parameter="pm25")

    assert peak is not None
    assert peak["station"] == "Anand Vihar"
    assert peak["value"] == 200.0
    assert peak["timestamp"] == "2026-09-19 12:00"


def test_compare_stations():
    """Verify station comparisons and sorting by mean concentration."""
    comparisons = compare_stations(SAMPLE_OBSERVATIONS)

    assert len(comparisons) == 2
    # Anand Vihar has mean 150.0, Pusa has mean 60.0 -> Anand Vihar first
    assert comparisons[0]["station"] == "Anand Vihar"
    assert comparisons[0]["pm25_mean"] == 150.0
    assert comparisons[0]["pm25_max"] == 200.0

    assert comparisons[1]["station"] == "Pusa"
    assert comparisons[1]["pm25_mean"] == 60.0
    assert comparisons[1]["pm25_max"] == 70.0


def test_detect_significant_changes():
    """Verify detection of rate-of-change jumps over threshold."""
    # Anand Vihar went from 100 to 150 (+50%)
    changes = detect_significant_changes(SAMPLE_OBSERVATIONS, parameter="pm25", threshold_pct=30.0)

    assert len(changes) > 0
    assert any("Anand Vihar: +50.0%" in c for c in changes)


def test_detect_missing_data():
    """Verify detection of data completeness gaps."""
    # We provided 3 timestamps, but expected 24 hours -> incomplete
    res = detect_missing_data(SAMPLE_OBSERVATIONS, expected_hours=24)

    assert res["status"] == "partial"
    assert len(res["sparse_stations"]) == 2
    assert res["average_completeness_pct"] < 25.0


def test_analyze_air_quality_end_to_end():
    """Verify master deterministic analytics bundle."""
    analytics = analyze_air_quality(SAMPLE_OBSERVATIONS, expected_hours=3)

    assert analytics["total_stations"] == 2
    assert analytics["total_observations"] == 6
    assert analytics["highest_station"] == "Anand Vihar"
    assert analytics["highest_avg_station"] == "Anand Vihar"
    assert analytics["peak_pollution"]["value"] == 200.0
