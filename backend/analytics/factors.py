from typing import List, Dict, Any, Tuple
from collections import Counter


def analyze_hotspot_factors(accidents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute contributing factors and temporal distributions per hotspot (FR-07).
    """
    total = len(accidents)
    if total == 0:
        return {
            "time_blocks": [0] * 8,
            "peak_time_text": "Not enough data",
            "factors": [],
        }

    # 1. Temporal 3-hour bins (12a-3a, 3a-6a, 6a-9a, 9a-12p, 12p-3p, 3p-6p, 6p-9p, 9p-12a)
    time_bins = [0] * 8
    weekday_counts = Counter()

    two_wheeler_count = 0
    poor_lighting_count = 0
    overspeeding_count = 0
    wet_road_count = 0
    pedestrian_count = 0

    for r in accidents:
        dt = r.get("occurred_at")
        if dt:
            hr = dt.hour if hasattr(dt, "hour") else 12
            bin_idx = min(7, hr // 3)
            time_bins[bin_idx] += 1
            if hasattr(dt, "weekday"):
                weekday_counts[dt.weekday()] += 1

        # Check vehicle types
        v_types = str(r.get("vehicle_types", "")).lower()
        if any(w in v_types for w in ["two-wheeler", "bike", "motorcycle", "scooter"]):
            two_wheeler_count += 1

        # Check light conditions
        light = str(r.get("light_condition", "")).lower()
        cause = str(r.get("probable_cause", "")).lower()
        if "dark" in light or "no streetlights" in light or "poor lighting" in cause:
            poor_lighting_count += 1

        # Check overspeeding
        if "speed" in cause or "rash" in cause or "overspeed" in cause:
            overspeeding_count += 1

        # Check wet road
        weather = str(r.get("weather", "")).lower()
        if "rain" in weather or "wet" in cause:
            wet_road_count += 1

        # Check pedestrian exposure
        if "pedestrian" in v_types or "crossing" in cause or "jaywalking" in cause:
            pedestrian_count += 1

    # Peak time determination
    max_bin_idx = time_bins.index(max(time_bins))
    bin_labels = [
        "12–3 am", "3–6 am", "6–9 am", "9–12 pm",
        "12–3 pm", "3–6 pm", "6–9 pm", "9–12 am"
    ]
    peak_hr = bin_labels[max_bin_idx]
    peak_time_text = f"{peak_hr}, Fri–Sat" if max_bin_idx >= 5 else f"{peak_hr}, Weekdays"

    factors = [
        {
            "factor_key": "two_wheelers",
            "label": "Two-wheelers involved",
            "count": two_wheeler_count,
            "percent": round((two_wheeler_count / total) * 100, 1),
        },
        {
            "factor_key": "poor_lighting",
            "label": "Poor lighting at night",
            "count": poor_lighting_count,
            "percent": round((poor_lighting_count / total) * 100, 1),
        },
        {
            "factor_key": "overspeeding",
            "label": "Overspeeding on approach",
            "count": overspeeding_count,
            "percent": round((overspeeding_count / total) * 100, 1),
        },
        {
            "factor_key": "wet_road",
            "label": "Wet road / poor drainage",
            "count": wet_road_count,
            "percent": round((wet_road_count / total) * 100, 1),
        },
        {
            "factor_key": "pedestrian_crossing",
            "label": "No safe pedestrian crossing",
            "count": pedestrian_count,
            "percent": round((pedestrian_count / total) * 100, 1),
        },
    ]

    # Sort factors by frequency percentage
    factors.sort(key=lambda x: x["percent"], reverse=True)

    return {
        "time_blocks": time_bins,
        "peak_time_text": peak_time_text,
        "factors": factors,
    }
