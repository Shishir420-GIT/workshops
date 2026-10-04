"""Deterministic air quality analytics engine in pure Python/Pandas.

Follows Lab 2 specifications:
- No LLM computation for numbers.
- Computes:
  - calculate_statistics()
  - find_peak_pollution()
  - compare_stations()
  - detect_missing_data()
  - detect_significant_changes()
  - analyze_air_quality()
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd


def _to_dataframe(data: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]]) -> pd.DataFrame:
    """Convert input observations into a clean, normalized Pandas DataFrame."""
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif isinstance(data, dict) and "observations" in data:
        df = pd.DataFrame(data["observations"])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame()

    if df.empty:
        return pd.DataFrame(columns=["station", "timestamp", "pm25", "pm10", "latitude", "longitude"])

    for col in ["station", "timestamp"]:
        if col not in df.columns:
            df[col] = "Unknown"

    for col in ["pm25", "pm10", "latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = None

    # Sort deterministically
    df["timestamp"] = df["timestamp"].astype(str)
    df = df.sort_values(by=["station", "timestamp"]).reset_index(drop=True)
    return df


def calculate_statistics(
    observations: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]],
    parameter: str = "pm25",
) -> Dict[str, Any]:
    """Calculate deterministic descriptive statistics for a pollutant.

    Args:
        observations: Observation records or DataFrame.
        parameter: 'pm25' or 'pm10'.

    Returns:
        Dict with min, max, mean, median, latest, count, time_of_max,
        earliest, change_pct_earliest_latest, hourly_averages.
    """
    df = _to_dataframe(observations)
    param = parameter.lower().replace(".", "").replace(" ", "")

    if df.empty or param not in df.columns or df[param].dropna().empty:
        return {
            "parameter": parameter,
            "min": 0.0,
            "max": 0.0,
            "mean": 0.0,
            "median": 0.0,
            "latest": 0.0,
            "count": 0,
            "time_of_max": None,
            "earliest": None,
            "change_pct_earliest_latest": None,
            "hourly_averages": {},
        }

    series = df[param].dropna()
    min_val = round(float(series.min()), 1)
    max_val = round(float(series.max()), 1)
    mean_val = round(float(series.mean()), 1)
    median_val = round(float(series.median()), 1)
    count_val = int(series.count())

    # Find time of maximum
    max_row = df.loc[df[param] == max_val].iloc[0]
    time_of_max = str(max_row.get("timestamp", ""))

    # Find earliest and latest measurements overall
    sorted_by_time = df.dropna(subset=[param]).sort_values(by="timestamp")
    earliest_val = round(float(sorted_by_time.iloc[0][param]), 1)
    latest_val = round(float(sorted_by_time.iloc[-1][param]), 1)

    change_pct = None
    if earliest_val > 0:
        change_pct = round(((latest_val - earliest_val) / earliest_val) * 100.0, 1)

    # Hourly grouping (averages by hour of day 00-23)
    hourly_averages: Dict[str, float] = {}
    try:
        df["hour"] = df["timestamp"].str.extract(r" (\d{2}):")[0]
        hour_grouped = df.groupby("hour")[param].mean().dropna()
        for hr, val in hour_grouped.items():
            hourly_averages[f"{hr}:00"] = round(float(val), 1)
    except Exception:
        pass

    return {
        "parameter": parameter,
        "min": min_val,
        "max": max_val,
        "mean": mean_val,
        "median": median_val,
        "latest": latest_val,
        "count": count_val,
        "time_of_max": time_of_max,
        "earliest": earliest_val,
        "change_pct_earliest_latest": change_pct,
        "hourly_averages": hourly_averages,
    }


def find_peak_pollution(
    observations: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]],
    parameter: str = "pm25",
) -> Optional[Dict[str, Any]]:
    """Find the single highest pollution event across all stations."""
    df = _to_dataframe(observations)
    param = parameter.lower().replace(".", "").replace(" ", "")

    if df.empty or param not in df.columns or df[param].dropna().empty:
        return None

    peak_row = df.sort_values(by=param, ascending=False).iloc[0]
    return {
        "station": str(peak_row["station"]),
        "parameter": parameter,
        "value": round(float(peak_row[param]), 1),
        "timestamp": str(peak_row["timestamp"]),
    }


def compare_stations(
    observations: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Compare air quality metrics across all monitoring stations."""
    df = _to_dataframe(observations)
    if df.empty or "station" not in df.columns:
        return []

    stations_summary = []
    for station, group in df.groupby("station"):
        item: Dict[str, Any] = {
            "station": str(station),
            "observation_count": len(group),
        }

        if "pm25" in group.columns and not group["pm25"].dropna().empty:
            pm25_s = group["pm25"].dropna()
            item["pm25_mean"] = round(float(pm25_s.mean()), 1)
            item["pm25_max"] = round(float(pm25_s.max()), 1)
            item["pm25_latest"] = round(float(pm25_s.iloc[-1]), 1)
        else:
            item["pm25_mean"] = None
            item["pm25_max"] = None
            item["pm25_latest"] = None

        if "pm10" in group.columns and not group["pm10"].dropna().empty:
            pm10_s = group["pm10"].dropna()
            item["pm10_mean"] = round(float(pm10_s.mean()), 1)
            item["pm10_max"] = round(float(pm10_s.max()), 1)
        else:
            item["pm10_mean"] = None
            item["pm10_max"] = None

        # Coordinates for mapping
        if "latitude" in group.columns and not group["latitude"].dropna().empty:
            item["latitude"] = float(group["latitude"].dropna().iloc[0])
            item["longitude"] = float(group["longitude"].dropna().iloc[0])

        stations_summary.append(item)

    # Sort descending by pm25_mean (or pm25_max)
    stations_summary.sort(
        key=lambda x: (x.get("pm25_mean") if x.get("pm25_mean") is not None else -1),
        reverse=True,
    )
    return stations_summary


def detect_missing_data(
    observations: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]],
    expected_hours: int = 24,
) -> Dict[str, Any]:
    """Detect gaps and assess data completeness for each station."""
    df = _to_dataframe(observations)
    if df.empty:
        return {"status": "no_data", "completeness_pct": 0.0, "sparse_stations": []}

    station_counts = df.groupby("station")["timestamp"].nunique().to_dict()
    sparse = []
    for station, count in station_counts.items():
        completeness = round((count / max(expected_hours, 1)) * 100.0, 1)
        if completeness < 80.0:
            sparse.append({
                "station": station,
                "recorded_hours": count,
                "expected_hours": expected_hours,
                "completeness_pct": completeness,
            })

    avg_completeness = (
        round(sum(station_counts.values()) / (len(station_counts) * max(expected_hours, 1)) * 100, 1)
        if station_counts
        else 0.0
    )

    return {
        "status": "complete" if not sparse else "partial",
        "average_completeness_pct": min(avg_completeness, 100.0),
        "total_stations": len(station_counts),
        "sparse_stations": sparse,
    }


def detect_significant_changes(
    observations: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]],
    parameter: str = "pm25",
    threshold_pct: float = 30.0,
) -> List[str]:
    """Detect sharp changes (> threshold_pct) between consecutive measurements."""
    df = _to_dataframe(observations)
    param = parameter.lower().replace(".", "").replace(" ", "")

    if df.empty or param not in df.columns:
        return []

    changes = []
    for station, group in df.groupby("station"):
        sorted_grp = group.dropna(subset=[param]).sort_values(by="timestamp")
        if len(sorted_grp) < 2:
            continue

        prev_row = None
        for _, curr_row in sorted_grp.iterrows():
            if prev_row is not None:
                prev_val = prev_row[param]
                curr_val = curr_row[param]
                if prev_val > 5.0:  # Ignore baseline noise near zero
                    diff_pct = ((curr_val - prev_val) / prev_val) * 100.0
                    if abs(diff_pct) >= threshold_pct:
                        direction = "+" if diff_pct > 0 else ""
                        changes.append(
                            f"{station}: {direction}{diff_pct:.1f}% between "
                            f"{prev_row['timestamp'][-5:]} ({prev_val:.0f}) and "
                            f"{curr_row['timestamp'][-5:]} ({curr_val:.0f} µg/m³)"
                        )
            prev_row = curr_row

    return changes


def analyze_air_quality(
    observations: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]],
    expected_hours: int = 24,
) -> Dict[str, Any]:
    """Execute complete deterministic analytics pipeline on air quality observations.

    Args:
        observations: Observation records from OpenAQ.
        expected_hours: Expected time window in hours.

    Returns:
        Structured analytics dictionary adhering to PRD requirements.
    """
    df = _to_dataframe(observations)
    pm25_stats = calculate_statistics(df, "pm25")
    pm10_stats = calculate_statistics(df, "pm10")
    peak_pm25 = find_peak_pollution(df, "pm25")
    comparisons = compare_stations(df)
    missing = detect_missing_data(df, expected_hours)
    sig_changes = detect_significant_changes(df, "pm25", threshold_pct=30.0)

    highest_station = comparisons[0]["station"] if comparisons else "None"
    highest_avg_station = (
        sorted(comparisons, key=lambda x: x.get("pm25_mean") or 0, reverse=True)[0]["station"]
        if comparisons
        else "None"
    )

    return {
        "total_stations": len(comparisons),
        "total_observations": len(df),
        "pm25_stats": pm25_stats,
        "pm10_stats": pm10_stats,
        "peak_pollution": peak_pm25,
        "station_comparisons": comparisons,
        "highest_station": highest_station,
        "highest_avg_station": highest_avg_station,
        "significant_changes": sig_changes,
        "data_completeness": missing,
    }
