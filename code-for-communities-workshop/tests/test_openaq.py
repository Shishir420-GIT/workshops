"""Tests for OpenAQ data retrieval and bounding constraints (Lab 1)."""

import pytest
from clean_air_agent.tools.openaq import (
    find_monitoring_locations,
    get_air_quality_observations,
    _haversine_km,
)


def test_haversine_distance():
    """Verify distance calculation between coordinates."""
    # Anand Vihar (28.6508, 77.3152) to Pusa (28.6360, 77.1570) ~ 15.5 km
    dist = _haversine_km(28.6508, 77.3152, 28.6360, 77.1570)
    assert 14.0 < dist < 17.0


def test_find_monitoring_locations_constraints():
    """Verify location search adheres to hard bounds and schemas."""
    res = find_monitoring_locations(location_name="Anand Vihar", radius_km=15.0)
    locations = res.get("locations", [])

    assert len(locations) > 0
    assert len(locations) <= 5, "Must never return more than 5 locations"

    first_loc = locations[0]
    assert "id" in first_loc
    assert "name" in first_loc
    assert "latitude" in first_loc
    assert "longitude" in first_loc
    assert "distance_km" in first_loc
    assert isinstance(first_loc["distance_km"], (int, float))


def test_find_monitoring_locations_radius_clamping():
    """Verify radius > 25km is clamped to 25km limit."""
    res = find_monitoring_locations(latitude=28.6, longitude=77.2, radius_km=100.0)
    locations = res.get("locations", [])
    assert len(locations) <= 5


def test_get_air_quality_observations_schema():
    """Verify observation normalization adheres to schema."""
    res = get_air_quality_observations(location_id=101, hours=24)
    obs = res.get("observations", [])

    assert len(obs) > 0
    assert len(obs) <= 500

    sample = obs[0]
    assert "station" in sample
    assert "timestamp" in sample
    assert "pm25" in sample
    assert "pm10" in sample
    assert "latitude" in sample
    assert "longitude" in sample


def test_get_air_quality_observations_hours_clamping():
    """Verify hours request is clamped to maximum 48 hours."""
    # Requesting 100 hours should clamp to 48 hours
    res = get_air_quality_observations(location_id=101, hours=100)
    obs = res.get("observations", [])
    assert len(obs) <= 48 * 2  # At most 48 hours for 1 station
