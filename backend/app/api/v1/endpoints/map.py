from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.accident import AccidentRecord
from app.models.hotspot import Hotspot
from analytics.hotspots import hotspot_detector

router = APIRouter(tags=["Geospatial Map"])


@router.get("/map/hotspots")
def get_map_hotspots(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
    risk_level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    unassigned_only: bool = Query(False),
) -> Any:
    """
    GeoJSON FeatureCollection of detected accident hotspots (FR-06).
    """
    query = db.query(Hotspot)
    if risk_level:
        query = query.filter(Hotspot.risk_level == risk_level)
    if status:
        query = query.filter(Hotspot.status == status)
    if unassigned_only:
        query = query.filter(Hotspot.assignee_id.is_(None))

    hotspots = query.all()

    features = []
    for h in hotspots:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [h.lon, h.lat],
            },
            "properties": {
                "id": h.id,
                "code": h.code,
                "name": h.name,
                "road_name": h.road_name,
                "area": h.area,
                "accidents_count": h.accidents_count,
                "fatalities": h.fatalities,
                "injured": h.injured,
                "risk_score": h.risk_score,
                "risk_level": h.risk_level,
                "risk_overridden": h.risk_overridden,
                "status": h.status,
                "assignee_id": h.assignee_id,
                "assignee_name": h.assignee.full_name if h.assignee else None,
                "peak_time_text": h.peak_time_text,
                "score_breakdown": h.score_breakdown,
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/map/accidents")
def get_map_accidents(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
    severity: Optional[str] = Query(None),
    road_type: Optional[str] = Query(None),
    limit: int = Query(500, le=2000),
) -> Any:
    """
    GeoJSON FeatureCollection of individual crash locations for authorized users (FR-06).
    """
    query = db.query(AccidentRecord)
    if severity:
        query = query.filter(AccidentRecord.severity.ilike(f"%{severity}%"))
    if road_type:
        query = query.filter(AccidentRecord.road_type == road_type)

    records = query.limit(limit).all()

    features = []
    for r in records:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r.longitude, r.latitude],
            },
            "properties": {
                "id": r.id,
                "code": r.accident_code,
                "occurred_at": r.occurred_at.isoformat() if r.occurred_at else None,
                "severity": r.severity,
                "fatalities": r.fatalities,
                "injuries": r.injuries,
                "road_name": r.road_name,
                "road_type": r.road_type,
                "location_text": r.location_text,
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/map/heat")
def get_map_heat(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> Any:
    """
    Precomputed 2D Gaussian Kernel Density Estimation (KDE) surface (FR-04, FR-06).
    """
    records = db.query(AccidentRecord).limit(1000).all()
    records_data = [{"latitude": r.latitude, "longitude": r.longitude} for r in records]
    return hotspot_detector.compute_kde_heat_grid(records_data)


@router.get("/map/layers")
def get_map_layers(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> Any:
    """
    Returns available geospatial layers and metadata (FR-06).
    """
    return {
        "layers": [
            {"id": "hotspots", "name": "Ranked Hotspots", "type": "point", "endpoint": "/api/v1/map/hotspots", "default": True},
            {"id": "accidents", "name": "Crash Points", "type": "point", "endpoint": "/api/v1/map/accidents", "default": True},
            {"id": "heat", "name": "KDE Crash Density", "type": "raster", "endpoint": "/api/v1/map/heat", "default": True},
        ]
    }


@router.get("/public/map")
@router.get("/map/public-grid")
def get_public_map(
    db: Session = Depends(get_db),
) -> Any:
    """
    Public aggregated hotspot map (BR-08, FR-12).
    STRICT PRIVACY ENFORCEMENT:
    - Snapped to coarse ~500m grid cells
    - Banded counts (10-19, 20-29, 30-39, 40+)
    - NO individual accident locations
    - NO victim names, timestamps or internal case assignment data
    """
    hotspots = db.query(Hotspot).all()

    areas = []
    for h in hotspots:
        # Snap coordinates to ~500m precision (0.005 degree ~ 550m)
        snapped_lat = round(h.lat / 0.005) * 0.005
        snapped_lon = round(h.lon / 0.005) * 0.005

        cnt = h.accidents_count
        if cnt >= 40:
            band = "40+ crashes"
        elif cnt >= 30:
            band = "30–39 crashes"
        elif cnt >= 20:
            band = "20–29 crashes"
        else:
            band = "10–19 crashes"

        areas.append({
            "id": h.id,
            "code": h.code,
            "area_name": h.name,
            "lat": round(snapped_lat, 4),
            "lon": round(snapped_lon, 4),
            "radius_approx_m": 500,
            "risk_level": h.risk_level,
            "accident_band": band,
            "safety_advisory": (
                "High density of pedestrian and two-wheeler movements. "
                "Reduce speed and observe signal indicators."
            ),
        })

    return {
        "title": "Public Hotspot Map",
        "description": "Combined, anonymized figures (Dec 2025 – Nov 2026). Areas snapped to 500m.",
        "areas": areas,
    }
