from typing import List, Dict, Any, Tuple

DEFAULT_WEIGHT_DEATHS = 0.45
DEFAULT_WEIGHT_FREQ = 0.35
DEFAULT_WEIGHT_INJ = 0.20

CRITICAL_THRESHOLD = 80
HIGH_THRESHOLD = 60
MEDIUM_THRESHOLD = 40


def calculate_risk_scores(
    clusters: List[Dict[str, Any]],
    weight_deaths: float = DEFAULT_WEIGHT_DEATHS,
    weight_freq: float = DEFAULT_WEIGHT_FREQ,
    weight_inj: float = DEFAULT_WEIGHT_INJ,
) -> List[Dict[str, Any]]:
    """
    Multi-criteria risk scoring and classification (FR-05).
    Formula: risk_score = 100 * (0.45*norm_deaths + 0.35*norm_freq + 0.20*norm_inj)
    Saves score point breakdown: {"deaths": pd, "frequency": pf, "injuries": pi}.
    """
    if not clusters:
        return []

    max_deaths = max(c["fatalities"] for c in clusters)
    max_freq = max(c["accidents_count"] for c in clusters)
    max_inj = max(c["injuries"] for c in clusters)

    # Prevent division by zero
    max_deaths = max(1, max_deaths)
    max_freq = max(1, max_freq)
    max_inj = max(1, max_inj)

    scored_clusters = []
    for c in clusters:
        norm_deaths = c["fatalities"] / max_deaths
        norm_freq = c["accidents_count"] / max_freq
        norm_inj = c["injuries"] / max_inj

        deaths_points = round(weight_deaths * 100 * norm_deaths)
        freq_points = round(weight_freq * 100 * norm_freq)
        inj_points = round(weight_inj * 100 * norm_inj)

        total_score = min(100, max(1, deaths_points + freq_points + inj_points))

        # Risk Classification
        if total_score >= CRITICAL_THRESHOLD:
            level = "critical"
        elif total_score >= HIGH_THRESHOLD:
            level = "high"
        elif total_score >= MEDIUM_THRESHOLD:
            level = "medium"
        else:
            level = "low"

        scored_item = dict(c)
        scored_item["risk_score"] = total_score
        scored_item["risk_level"] = level
        scored_item["score_breakdown"] = {
            "deaths": deaths_points,
            "frequency": freq_points,
            "injuries": inj_points,
        }
        scored_clusters.append(scored_item)

    # Sort descending by risk score
    scored_clusters.sort(key=lambda x: x["risk_score"], reverse=True)
    return scored_clusters
