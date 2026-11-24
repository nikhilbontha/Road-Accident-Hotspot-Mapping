import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from analytics.geocoding import geocoder

SEVERITY_STANDARDIZATION = {
    "grevious": "Grievous injury",
    "grevious injury": "Grievous injury",
    "grievous": "Grievous injury",
    "grievous injury": "Grievous injury",
    "fatal": "Fatal",
    "fatality": "Fatal",
    "death": "Fatal",
    "minor": "Minor injury",
    "minor injury": "Minor injury",
    "simple": "Minor injury",
    "simple injury": "Minor injury",
    "non-injury": "Non-injury",
    "non injury": "Non-injury",
    "property damage": "Non-injury",
    "no injury": "Non-injury",
}

WEATHER_STANDARDIZATION = {
    "foggy": "Fog",
    "fog": "Fog",
    "rainy": "Rain",
    "rain": "Rain",
    "heavy rain": "Rain",
    "clear": "Clear",
    "sunny": "Clear",
    "cloudy": "Cloudy",
}

LIGHT_STANDARDIZATION = {
    "day": "Daylight",
    "daylight": "Daylight",
    "night": "Dark: Streetlights on",
    "night dark": "Dark: No streetlights",
    "dark": "Dark: No streetlights",
    "dusk": "Dusk / Dawn",
    "dawn": "Dusk / Dawn",
}


def parse_date_time(date_str: Any, time_str: Any) -> Tuple[Optional[datetime], Optional[str]]:
    """
    Parse date and time strings. Returns (datetime_obj, error_message).
    """
    if not date_str or str(date_str).strip() == "":
        return None, "Missing accident date"

    # Normalize date
    d_clean = str(date_str).strip()
    t_clean = str(time_str).strip() if time_str else "12:00"

    # Check for invalid time formats like '25:10'
    time_match = re.match(r"^(\d{1,2}):(\d{2})(?::\d{2})?$", t_clean)
    if time_match:
        hr, mn = int(time_match.group(1)), int(time_match.group(2))
        if hr < 0 or hr > 23 or mn < 0 or mn > 59:
            return None, f"Invalid time '{t_clean}' (hours must be 0-23, minutes 0-59)"
    else:
        # If it's a date object or timestamp string
        t_clean = "12:00"

    combined = f"{d_clean} {t_clean}"
    for fmt in [
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]:
        try:
            return datetime.strptime(combined.split(".")[0], fmt), None
        except ValueError:
            continue

    return None, f"Invalid date format '{date_str}'"


def validate_accident_row(
    row: Dict[str, Any],
    row_number: int,
    seen_codes: set,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Validate a single sanitized accident row.
    Returns (cleaned_row, issues_list, row_status).
    row_status is one of: 'ready', 'corrected', 'rejected'
    """
    issues = []
    cleaned = dict(row)
    status = "ready"

    # 1. Check Accident Code & Duplicates
    code = cleaned.get("accident_code") or cleaned.get("id") or cleaned.get("record_id")
    if not code:
        code = f"ACC-2026-{10000 + row_number}"
        cleaned["accident_code"] = code
    else:
        code = str(code).strip()
        cleaned["accident_code"] = code

    if code in seen_codes:
        issues.append({
            "row_number": row_number,
            "issue_type": "duplicate",
            "field": "accident_code",
            "message": f"Duplicate of {code}",
            "suggested_fix": "Skip duplicate record",
            "action": "skip",
        })
        status = "rejected"
    else:
        seen_codes.add(code)

    # 2. Date and Time Validation
    raw_date = cleaned.get("date") or cleaned.get("occurred_at") or cleaned.get("accident_date")
    raw_time = cleaned.get("time") or cleaned.get("accident_time")
    dt_obj, dt_err = parse_date_time(raw_date, raw_time)

    if dt_err:
        issues.append({
            "row_number": row_number,
            "issue_type": "invalid_date_time",
            "field": "date/time",
            "message": dt_err,
            "suggested_fix": "Correct to valid timestamp or default 12:00",
            "action": "fix",
        })
        status = "rejected"
        cleaned["occurred_at"] = datetime(2026, 1, 1, 12, 0)
    else:
        cleaned["occurred_at"] = dt_obj

    # 3. Location & Coordinate Validation
    loc_text = str(cleaned.get("location") or cleaned.get("location_text") or cleaned.get("road_name") or "Unknown Location").strip()
    cleaned["location_text"] = loc_text

    raw_lat = cleaned.get("latitude") or cleaned.get("lat")
    raw_lon = cleaned.get("longitude") or cleaned.get("lon") or cleaned.get("lng")

    lat, lon, conf = None, None, 1.0

    if raw_lat is not None and raw_lon is not None and str(raw_lat).strip() and str(raw_lon).strip():
        try:
            parsed_lat = float(raw_lat)
            parsed_lon = float(raw_lon)
            # Valid coordinate bounds for India / Telangana region
            if 8.0 <= parsed_lat <= 36.0 and 68.0 <= parsed_lon <= 98.0:
                lat, lon, conf = parsed_lat, parsed_lon, 1.0
            else:
                issues.append({
                    "row_number": row_number,
                    "issue_type": "invalid_coordinate",
                    "field": "latitude/longitude",
                    "message": f"Latitude outside valid range ({parsed_lat}, {parsed_lon})",
                    "suggested_fix": "Geocode location description automatically",
                    "action": "fix",
                })
                # Fallback geocode
                lat, lon, conf = geocoder.geocode(loc_text)
                status = "corrected" if status != "rejected" else "rejected"
        except (ValueError, TypeError):
            lat, lon, conf = geocoder.geocode(loc_text)
            status = "corrected" if status != "rejected" else "rejected"
    else:
        # Address-only match
        lat, lon, conf = geocoder.geocode(loc_text)
        issues.append({
            "row_number": row_number,
            "issue_type": "address_only",
            "field": "coordinates",
            "message": f"Address-only match {int(conf * 100)}%",
            "suggested_fix": f"Accept estimated coordinates ({lat:.4f}, {lon:.4f})",
            "action": "accept",
        })
        status = "corrected" if status != "rejected" else "rejected"

    cleaned["latitude"] = lat if lat is not None else 17.4125
    cleaned["longitude"] = lon if lon is not None else 78.5721
    cleaned["geocode_confidence"] = conf

    # 4. Severity Validation & Standardization
    raw_sev = str(cleaned.get("severity") or "minor").strip().lower()
    std_sev = SEVERITY_STANDARDIZATION.get(raw_sev)
    if std_sev:
        if raw_sev in ["grevious", "grievous"]:
            issues.append({
                "row_number": row_number,
                "issue_type": "spelling_correction",
                "field": "severity",
                "message": f"'{cleaned.get('severity')}' standardized to 'Grievous injury'",
                "suggested_fix": "Auto-corrected for you",
                "action": "done",
            })
            status = "corrected" if status != "rejected" else "rejected"
        cleaned["severity"] = std_sev
    else:
        cleaned["severity"] = "Minor injury"

    # 5. Fatalities and Injuries check (non-negative)
    try:
        fat = int(cleaned.get("fatalities", 0))
        if fat < 0:
            issues.append({
                "row_number": row_number,
                "issue_type": "negative_value",
                "field": "fatalities",
                "message": f"Negative fatalities ({fat})",
                "suggested_fix": "Change to 0",
                "action": "fix",
            })
            fat = 0
            status = "rejected"
        cleaned["fatalities"] = fat
    except (ValueError, TypeError):
        cleaned["fatalities"] = 0

    try:
        inj = int(cleaned.get("injuries", 0))
        if inj < 0:
            issues.append({
                "row_number": row_number,
                "issue_type": "negative_value",
                "field": "injuries",
                "message": f"Negative injuries ({inj})",
                "suggested_fix": "Change to 0",
                "action": "fix",
            })
            inj = 0
            status = "rejected"
        cleaned["injuries"] = inj
    except (ValueError, TypeError):
        cleaned["injuries"] = 0

    # Standardize weather / light
    w = str(cleaned.get("weather", "Clear")).strip().lower()
    cleaned["weather"] = WEATHER_STANDARDIZATION.get(w, "Clear")

    l = str(cleaned.get("light_condition", "Daylight")).strip().lower()
    cleaned["light_condition"] = LIGHT_STANDARDIZATION.get(l, "Daylight")

    return cleaned, issues, status
