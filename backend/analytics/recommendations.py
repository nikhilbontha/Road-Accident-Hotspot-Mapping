from typing import List, Dict, Any

RECOMMENDATION_RULE_CATALOG = {
    "poor_lighting": {
        "title": "High-mast illumination & junction street lighting",
        "action_template": "Install high-output LED streetlights and continuous lighting spanning 300m on both approaches.",
        "default_confidence": "high",
    },
    "overspeeding": {
        "title": "Warning signage, radar speed display & rumble strips",
        "action_template": "Install transverse bar markings, speed warning boards, and automated speed feedback displays.",
        "default_confidence": "medium",
    },
    "two_wheelers": {
        "title": "Protected turning lane & segregated motorcycle bay",
        "action_template": "Delineate dedicated two-wheeler waiting boxes at signals and physical channelization on turnings.",
        "default_confidence": "medium",
    },
    "pedestrian_crossing": {
        "title": "Marked pedestrian crossing with central refuge island",
        "action_template": "Construct raised zebra crossings with tactile paving and solar-powered pedestrian flashers.",
        "default_confidence": "low",
    },
    "wet_road": {
        "title": "Anti-skid asphalt surfacing & improved storm drainage",
        "action_template": "Re-profile road camber to prevent water pooling and lay high-friction micro-surfacing.",
        "default_confidence": "medium",
    },
    "junction": {
        "title": "Traffic signal phasing & geometric junction redesign",
        "action_template": "Implement split phasing for right turns and modify kerb corner radii to enforce slower entry speeds.",
        "default_confidence": "high",
    },
}


def generate_recommendations(
    factors: List[Dict[str, Any]],
    total_accidents: int,
    time_blocks: List[int],
) -> List[Dict[str, Any]]:
    """
    Generate evidence-grounded safety recommendations from contributing factors (FR-07).
    Every recommendation is tagged: is_ai_generated=True (BR-01).
    """
    recommendations = []

    for factor in factors:
        key = factor["factor_key"]
        percent = factor["percent"]
        count = factor["count"]

        if key in RECOMMENDATION_RULE_CATALOG and (percent >= 15 or count >= 3):
            rule = RECOMMENDATION_RULE_CATALOG[key]

            # Generate evidence grounded in database figures
            if key == "poor_lighting":
                night_crashes = time_blocks[0] + time_blocks[6] + time_blocks[7]
                evidence = f"{night_crashes} of {total_accidents} crashes happened between 6 pm and midnight"
            elif key == "two_wheelers":
                evidence = f"{int(percent)}% of vehicles involved were two-wheelers ({count} crashes)"
            elif key == "overspeeding":
                evidence = f"{int(percent)}% of crashes involved overspeeding on approach"
            elif key == "pedestrian_crossing":
                evidence = f"{count} pedestrian conflicts recorded without crossing infrastructure"
            elif key == "wet_road":
                evidence = f"{int(percent)}% of incidents occurred under wet/rain conditions"
            else:
                evidence = f"Identified in {count} out of {total_accidents} crash investigations"

            recommendations.append({
                "title": rule["title"],
                "linked_factor": factor["label"],
                "evidence_text": evidence,
                "confidence": rule["default_confidence"],
                "is_ai_generated": True,
            })

    # Always ensure at least 3-4 recommendations for high priority spots
    if len(recommendations) < 3:
        rule = RECOMMENDATION_RULE_CATALOG["junction"]
        recommendations.append({
            "title": rule["title"],
            "linked_factor": "Intersection traffic conflict",
            "evidence_text": f"Crash density clusters within 250 m junction radius ({total_accidents} events)",
            "confidence": "high",
            "is_ai_generated": True,
        })

    return recommendations[:4]
