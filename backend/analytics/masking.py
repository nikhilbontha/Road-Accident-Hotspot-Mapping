import re
from typing import Tuple, Dict, Any, List

# Indian Vehicle Registration Number regex pattern:
# Format: [State Code 2 letters][District Code 1-2 digits][Series 0-3 letters][Number 1-4 digits]
# Examples: TS09AB1234, AP 28 XY 9999, MH-12-CD-5678, DL 1A 1234
VEHICLE_REGEX = re.compile(
    r"\b[A-Z]{2}[ -]?[0-9]{1,2}[ -]?[A-Z]{0,3}[ -]?[0-9]{1,4}\b",
    re.IGNORECASE,
)

# Indian 10-digit mobile phone numbers and standard telephone patterns:
# Examples: +91 9876543210, 09876543210, 9876543210, 8123456789
PHONE_REGEX = re.compile(
    r"(?:\+91[\s-]*)?(?:0)?[6-9]\d{4}[\s-]?\d{5}\b",
)

# Indian Driving Licence pattern:
# Format: 2-letter state code + 2-digit RTO/year code + digits
DL_REGEX = re.compile(
    r"\b[A-Z]{2}[0-9]{2}\s?[0-9]{4,11}\b",
    re.IGNORECASE,
)

# PII-sensitive column names to drop or mask completely
PII_COLUMNS = {
    "name",
    "driver_name",
    "victim_name",
    "owner_name",
    "phone",
    "mobile",
    "contact",
    "phone_number",
    "vehicle_number",
    "reg_number",
    "registration_no",
    "licence_number",
    "license_no",
    "aadhaar",
    "address_home",
}


def mask_sensitive_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Mask vehicle numbers, phone numbers, and license numbers from arbitrary text.
    Returns (masked_text, counts_dict).
    """
    if not isinstance(text, str):
        return text, {"vehicle_numbers": 0, "phone_numbers": 0, "names": 0}

    counts = {"vehicle_numbers": 0, "phone_numbers": 0, "names": 0}

    def replace_phone(match):
        counts["phone_numbers"] += 1
        return "[MASKED_PHONE]"

    def replace_vehicle(match):
        token = match.group(0).strip()
        # Ensure it looks like a vehicle plate (contains at least one letter and one number)
        if re.search(r"[A-Za-z]", token) and re.search(r"[0-9]", token) and len(token) >= 6:
            counts["vehicle_numbers"] += 1
            return "[MASKED_VEHICLE]"
        return token

    # Mask phones
    masked = PHONE_REGEX.sub(replace_phone, text)

    # Mask vehicle registration numbers
    masked = VEHICLE_REGEX.sub(replace_vehicle, masked)

    return masked, counts


def sanitize_row(row_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    """
    Sanitize row data prior to any storage or LLM processing (BR-03, FR-12).
    Drops or masks personal identifiers and tallies counts.
    """
    cleaned = {}
    counts = {"vehicle_numbers": 0, "phone_numbers": 0, "names": 0}

    for col, val in row_dict.items():
        col_lower = str(col).strip().lower()

        # If column is an explicit PII identifier column
        if col_lower in PII_COLUMNS or any(pii in col_lower for pii in ["name", "driver", "victim", "owner"]):
            if val is not None and str(val).strip():
                if any(x in col_lower for x in ["vehicle", "reg"]):
                    counts["vehicle_numbers"] += 1
                elif any(x in col_lower for x in ["phone", "mobile", "contact"]):
                    counts["phone_numbers"] += 1
                else:
                    counts["names"] += 1
            # Do NOT store raw personal identity
            continue

        # For text columns (like location_text or probable_cause), scrub any embedded PII
        if isinstance(val, str):
            masked_val, text_counts = mask_sensitive_text(val)
            for k in counts:
                counts[k] += text_counts[k]
            cleaned[col] = masked_val
        else:
            cleaned[col] = val

    return cleaned, counts
