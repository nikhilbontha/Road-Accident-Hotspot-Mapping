import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.db import get_db
from app.api import deps
from app.models.accident import AccidentRecord
from app.models.audit import AuditLog
from app.models.user import User, UserRoleEnum

router = APIRouter(prefix="/accidents", tags=["Accidents"])

class AccidentCreate(BaseModel):
    accident_code: Optional[str] = None
    occurred_at: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_text: str = Field(..., min_length=2)
    severity: str = Field(default="minor_injury")  # fatal, grievous_injury, minor_injury, non_injury
    fatalities: int = Field(default=0, ge=0)
    injuries: int = Field(default=0, ge=0)
    road_name: Optional[str] = None
    road_type: Optional[str] = "city_road"
    weather: Optional[str] = "Clear"
    light_condition: Optional[str] = "Daylight"
    probable_cause: Optional[str] = None
    vehicle_types: Optional[List[str]] = Field(default_factory=list)

class AccidentUpdate(BaseModel):
    location_text: Optional[str] = None
    severity: Optional[str] = None
    fatalities: Optional[int] = Field(None, ge=0)
    injuries: Optional[int] = Field(None, ge=0)
    weather: Optional[str] = None
    road_type: Optional[str] = None
    light_condition: Optional[str] = None
    probable_cause: Optional[str] = None

@router.get("")
def list_accidents(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    road_type: Optional[str] = Query(None),
    weather: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    query = db.query(AccidentRecord)

    if date_from:
        query = query.filter(AccidentRecord.occurred_at >= date_from)
    if date_to:
        query = query.filter(AccidentRecord.occurred_at <= date_to)
    if severity:
        query = query.filter(AccidentRecord.severity.ilike(severity))
    if road_type:
        query = query.filter(AccidentRecord.road_type.ilike(road_type))
    if weather:
        query = query.filter(AccidentRecord.weather.ilike(weather))

    total = query.count()
    records = query.order_by(AccidentRecord.occurred_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": r.id,
                "accident_code": r.accident_code,
                "occurred_at": r.occurred_at.isoformat() if r.occurred_at else None,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "location_text": r.location_text,
                "severity": r.severity,
                "fatalities": r.fatalities,
                "injuries": r.injuries,
                "road_name": r.road_name,
                "road_type": r.road_type,
                "weather": r.weather,
                "light_condition": r.light_condition,
                "probable_cause": r.probable_cause,
                "vehicle_types": r.vehicle_types or []
            }
            for r in records
        ]
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def create_accident(
    payload: AccidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        deps.require_roles([UserRoleEnum.ADMIN, UserRoleEnum.POLICE_OFFICER, UserRoleEnum.SAFETY_ANALYST])
    )
) -> Dict[str, Any]:
    code = payload.accident_code or f"ACC-MAN-{uuid.uuid4().hex[:8].upper()}"

    # Check unique code
    existing = db.query(AccidentRecord).filter(AccidentRecord.accident_code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Accident code already exists")

    rec = AccidentRecord(
        id=str(uuid.uuid4()),
        accident_code=code,
        occurred_at=payload.occurred_at,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_text=payload.location_text,
        severity=payload.severity,
        fatalities=payload.fatalities,
        injuries=payload.injuries,
        road_name=payload.road_name,
        road_type=payload.road_type,
        weather=payload.weather,
        light_condition=payload.light_condition,
        probable_cause=payload.probable_cause,
        vehicle_types=payload.vehicle_types,
        geocode_confidence=1.0
    )
    db.add(rec)

    # Log to audit trail
    audit = AuditLog(
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action="accident_created",
        entity_type="accident_record",
        entity_id=rec.id,
        after_state={"code": rec.accident_code, "severity": rec.severity, "location": rec.location_text},
        reason="Manual accident entry"
    )
    db.add(audit)
    db.commit()
    db.refresh(rec)

    return {
        "id": rec.id,
        "accident_code": rec.accident_code,
        "occurred_at": rec.occurred_at.isoformat(),
        "latitude": rec.latitude,
        "longitude": rec.longitude,
        "location_text": rec.location_text,
        "severity": rec.severity,
        "fatalities": rec.fatalities,
        "injuries": rec.injuries
    }

@router.get("/{accident_id}")
def get_accident(
    accident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    rec = db.query(AccidentRecord).filter(
        (AccidentRecord.id == accident_id) | (AccidentRecord.accident_code == accident_id)
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Accident record not found")

    return {
        "id": rec.id,
        "accident_code": rec.accident_code,
        "occurred_at": rec.occurred_at.isoformat() if rec.occurred_at else None,
        "latitude": rec.latitude,
        "longitude": rec.longitude,
        "location_text": rec.location_text,
        "severity": rec.severity,
        "fatalities": rec.fatalities,
        "injuries": rec.injuries,
        "road_name": rec.road_name,
        "road_type": rec.road_type,
        "weather": rec.weather,
        "light_condition": rec.light_condition,
        "probable_cause": rec.probable_cause,
        "vehicle_types": rec.vehicle_types or [],
        "geocode_confidence": rec.geocode_confidence
    }

@router.patch("/{accident_id}")
def update_accident(
    accident_id: str,
    payload: AccidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        deps.require_roles([UserRoleEnum.ADMIN, UserRoleEnum.POLICE_OFFICER, UserRoleEnum.SAFETY_ANALYST])
    )
) -> Dict[str, Any]:
    rec = db.query(AccidentRecord).filter(
        (AccidentRecord.id == accident_id) | (AccidentRecord.accident_code == accident_id)
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Accident record not found")

    before_state = {"severity": rec.severity, "fatalities": rec.fatalities, "injuries": rec.injuries}
    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(rec, field, val)

    # Log to audit trail
    audit = AuditLog(
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        action="accident_updated",
        entity_type="accident_record",
        entity_id=rec.id,
        before_state=before_state,
        after_state=update_data,
        reason="Field record correction"
    )
    db.add(audit)
    db.commit()
    db.refresh(rec)

    return {"status": "updated", "id": rec.id, "accident_code": rec.accident_code}
