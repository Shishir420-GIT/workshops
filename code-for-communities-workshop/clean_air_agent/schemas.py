"""Pydantic data models and schemas for Clean Air Investigator."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MonitoringLocation(BaseModel):
    """Air quality monitoring station metadata."""
    id: int
    name: str
    latitude: float
    longitude: float
    distance_km: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None


class Observation(BaseModel):
    """A normalized air quality observation from a monitoring station."""
    station: str
    timestamp: str
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PollutantStats(BaseModel):
    """Deterministic statistical summary for a single pollutant."""
    parameter: str
    min: float
    max: float
    mean: float
    median: float
    latest: float
    count: int
    time_of_max: Optional[str] = None
    earliest: Optional[float] = None
    change_pct_earliest_latest: Optional[float] = None
    hourly_averages: Dict[str, float] = Field(default_factory=dict)


class PeakPollution(BaseModel):
    """Peak pollution event details."""
    station: str
    parameter: str
    value: float
    timestamp: str


class StationComparison(BaseModel):
    """Comparative metrics for a single monitoring station."""
    station: str
    pm25_mean: Optional[float] = None
    pm25_max: Optional[float] = None
    pm25_latest: Optional[float] = None
    pm10_mean: Optional[float] = None
    pm10_max: Optional[float] = None
    observation_count: int = 0


class AirQualityAnalytics(BaseModel):
    """Full deterministic analytics payload computed by Python."""
    total_stations: int
    total_observations: int
    pm25_stats: Optional[PollutantStats] = None
    pm10_stats: Optional[PollutantStats] = None
    peak_pollution: Optional[PeakPollution] = None
    station_comparisons: List[StationComparison] = Field(default_factory=list)
    significant_changes: List[str] = Field(default_factory=list)
    data_completeness: Dict[str, Any] = Field(default_factory=dict)


class InvestigationEvidence(BaseModel):
    """Structured evidence package provided to Gemini for interpretation."""
    target_location: str
    time_window_hours: int
    stations: List[MonitoringLocation]
    analytics: AirQualityAnalytics


class InvestigationReport(BaseModel):
    """Structured 4-part investigation report produced by Gemini reasoning."""
    observed: List[str] = Field(
        description="Directly supported factual observations from measurements only."
    )
    pattern: List[str] = Field(
        description="Calculated statistical patterns or temporal trends."
    )
    possible_contributing_factors: List[str] = Field(
        description="Hypotheses regarding environmental or atmospheric factors (explicitly labeled as possibilities)."
    )
    further_investigation: List[str] = Field(
        description="Recommended next steps and additional data needs."
    )


class ValidationResult(BaseModel):
    """Result of deterministic output validation on Gemini's response."""
    is_safe: bool
    issues: List[str] = Field(default_factory=list)
    flags: Dict[str, bool] = Field(default_factory=dict)
    sanitized_text: str = ""
