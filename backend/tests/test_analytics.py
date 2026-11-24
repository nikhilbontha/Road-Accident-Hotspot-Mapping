import time
import pytest
import numpy as np
from analytics.hotspots import hotspot_detector, project_to_meters
from analytics.scoring import calculate_risk_scores
from analytics.factors import analyze_hotspot_factors
from analytics.recommendations import generate_recommendations


def test_dbscan_clustering_seeded_clusters():
    # Seed Cluster 1: NH-65 (10 accidents around 17.4125, 78.5721)
    cluster1 = [
        {
            "accident_code": f"C1-{i}",
            "latitude": 17.4125 + np.random.uniform(-0.0005, 0.0005),
            "longitude": 78.5721 + np.random.uniform(-0.0005, 0.0005),
            "road_name": "NH-65 × Station Road Junction",
            "fatalities": 1 if i < 3 else 0,
            "injuries": 2,
        }
        for i in range(10)
    ]

    # Seed Cluster 2: Outer Ring Road (8 accidents around 17.4890, 78.6120)
    cluster2 = [
        {
            "accident_code": f"C2-{i}",
            "latitude": 17.4890 + np.random.uniform(-0.0005, 0.0005),
            "longitude": 78.6120 + np.random.uniform(-0.0005, 0.0005),
            "road_name": "Outer Ring Road, Exit 12",
            "fatalities": 2 if i < 2 else 0,
            "injuries": 1,
        }
        for i in range(8)
    ]

    # Scattered Noise (3 isolated points)
    noise = [
        {"accident_code": f"N-{i}", "latitude": 17.3000 + i * 0.05, "longitude": 78.3000 + i * 0.05}
        for i in range(3)
    ]

    dataset = cluster1 + cluster2 + noise
    clusters, err = hotspot_detector.detect_clusters(dataset, radius_m=250.0, min_accidents=5)

    assert err is None
    assert len(clusters) == 2

    c_names = {c["name"] for c in clusters}
    assert "NH-65 × Station Road Junction" in c_names
    assert "Outer Ring Road, Exit 12" in c_names


def test_insufficient_data_rule():
    # Only 3 records (threshold is 5)
    scarce_records = [
        {"latitude": 17.4125, "longitude": 78.5721, "fatalities": 0, "injuries": 1},
        {"latitude": 17.4130, "longitude": 78.5725, "fatalities": 0, "injuries": 0},
        {"latitude": 17.4120, "longitude": 78.5718, "fatalities": 1, "injuries": 0},
    ]

    clusters, err = hotspot_detector.detect_clusters(scarce_records, radius_m=250.0, min_accidents=5)
    assert len(clusters) == 0
    assert err == "No reliable hotspot can be determined from this data"


def test_risk_scoring_and_breakdown():
    clusters = [
        {
            "name": "High Severity Spot",
            "accidents_count": 40,
            "fatalities": 8,
            "injuries": 50,
        },
        {
            "name": "Low Severity Spot",
            "accidents_count": 8,
            "fatalities": 0,
            "injuries": 4,
        },
    ]

    scored = calculate_risk_scores(clusters)
    assert len(scored) == 2

    top = scored[0]
    assert top["risk_level"] in ["critical", "high"]
    assert "deaths" in top["score_breakdown"]
    assert "frequency" in top["score_breakdown"]
    assert "injuries" in top["score_breakdown"]
    breakdown_sum = sum(top["score_breakdown"].values())
    assert abs(top["risk_score"] - breakdown_sum) <= 1


def test_factor_analysis_and_recommendations():
    from datetime import datetime
    accidents = [
        {
            "occurred_at": datetime(2026, 5, 14, 20, 30),  # 8-11pm -> bin 6
            "vehicle_types": "Two-wheeler;Car",
            "light_condition": "Dark: No streetlights",
            "probable_cause": "Overspeeding in dark",
            "weather": "Clear",
        }
        for _ in range(10)
    ]

    analysis = analyze_hotspot_factors(accidents)
    assert "time_blocks" in analysis
    assert len(analysis["time_blocks"]) == 8
    assert "factors" in analysis

    recs = generate_recommendations(
        factors=analysis["factors"],
        total_accidents=10,
        time_blocks=analysis["time_blocks"],
    )
    assert len(recs) >= 1
    for r in recs:
        assert r["is_ai_generated"] is True
        assert r["confidence"] in ["high", "medium", "low"]
        assert len(r["evidence_text"]) > 5


def test_performance_50000_records_benchmark():
    """
    Benchmark test verifying processing of 50,000 synthetic records <= 120 seconds (BRD §9, FR-04).
    """
    print("\nGenerating 50,000 synthetic records...")
    np.random.seed(42)
    n = 50000

    # 10 cluster centers around Hyderabad
    centers = [
        (17.4125, 78.5721),
        (17.4890, 78.6120),
        (17.3980, 78.4720),
        (17.4420, 78.3810),
        (17.4310, 78.5310),
        (17.4250, 78.4890),
        (17.4650, 78.5200),
        (17.3610, 78.4750),
        (17.4100, 78.5900),
        (17.4350, 78.5020),
    ]

    lats = []
    lons = []
    for _ in range(n):
        c = centers[np.random.randint(0, len(centers))]
        # Gaussian spread around center
        lats.append(c[0] + np.random.normal(0, 0.003))
        lons.append(c[1] + np.random.normal(0, 0.003))

    records = [
        {
            "latitude": lats[i],
            "longitude": lons[i],
            "road_name": f"Road Segment {i % 10}",
            "fatalities": np.random.choice([0, 1], p=[0.9, 0.1]),
            "injuries": np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1]),
        }
        for i in range(n)
    ]

    start_time = time.time()
    clusters, err = hotspot_detector.detect_clusters(records, radius_m=250.0, min_accidents=10)
    scored = calculate_risk_scores(clusters)
    elapsed = time.time() - start_time

    print(f"\n[BENCHMARK RESULT] 50,000 records processed in: {elapsed:.2f} seconds.")
    print(f"Hotspots detected: {len(clusters)}")
    assert elapsed <= 120.0, f"Performance target exceeded: {elapsed:.2f}s > 120.0s"
