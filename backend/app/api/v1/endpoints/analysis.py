from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_active_user, require_roles
from app.models.user import User, UserRoleEnum
from app.models.system import AnalysisRun, SystemSetting
from app.services.hotspot_service import hotspot_service

router = APIRouter(prefix="/analysis", tags=["Hotspot Analysis"])


class AnalysisRunRequest(BaseModel):
    radius_m: Optional[float] = 250.0
    min_accidents: Optional[int] = 5
    period_months: Optional[int] = 12


class SettingsUpdateRequest(BaseModel):
    radius_m: Optional[float] = None
    min_accidents: Optional[int] = None
    weight_deaths: Optional[float] = None
    weight_frequency: Optional[float] = None
    weight_injuries: Optional[float] = None
    critical_threshold: Optional[int] = None
    high_threshold: Optional[int] = None
    medium_threshold: Optional[int] = None


@router.post("/runs", status_code=status.HTTP_200_OK)
def trigger_analysis(
    params: AnalysisRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN, UserRoleEnum.POLICE_OFFICER, UserRoleEnum.SAFETY_ANALYST])),
) -> Any:
    """
    Run hotspot detection and multi-criteria risk scoring (FR-04, FR-05, BR-05).
    """
    result = hotspot_service.run_analysis(
        db=db,
        actor_id=current_user.id,
        radius_m=params.radius_m or 250.0,
        min_accidents=params.min_accidents or 5,
        period_months=params.period_months or 12,
    )
    return result


@router.get("/runs/{run_id}")
def get_analysis_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get status and parameters of a previous analysis run (FR-04).
    """
    run = db.query(AnalysisRun).filter(
        (AnalysisRun.id == run_id) | (AnalysisRun.run_number == run_id)
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return {
        "id": run.id,
        "run_number": run.run_number,
        "parameters": run.parameters,
        "status": run.status,
        "record_count": run.record_count,
        "duration_ms": run.duration_ms,
        "created_at": run.created_at,
    }


@router.get("/settings")
def get_analysis_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get system scoring weights and risk thresholds (FR-05).
    """
    setting = db.query(SystemSetting).filter(SystemSetting.key == "analysis_weights").first()
    if setting:
        return setting.value

    return {
        "radius_m": 250,
        "min_accidents": 5,
        "weight_deaths": 0.45,
        "weight_frequency": 0.35,
        "weight_injuries": 0.20,
        "critical_threshold": 80,
        "high_threshold": 60,
        "medium_threshold": 40,
    }


@router.put("/settings")
def update_analysis_settings(
    update_data: SettingsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN])),
) -> Any:
    """
    Admin updates algorithm parameters, scoring weights, and thresholds (FR-05).
    """
    setting = db.query(SystemSetting).filter(SystemSetting.key == "analysis_weights").first()
    current = setting.value if setting else {
        "radius_m": 250,
        "min_accidents": 5,
        "weight_deaths": 0.45,
        "weight_frequency": 0.35,
        "weight_injuries": 0.20,
        "critical_threshold": 80,
        "high_threshold": 60,
        "medium_threshold": 40,
    }

    for k, v in update_data.model_dump(exclude_unset=True).items():
        current[k] = v

    if not setting:
        setting = SystemSetting(key="analysis_weights", value=current)
        db.add(setting)
    else:
        setting.value = current

    db.commit()
    return {"message": "Analysis parameters updated successfully", "settings": current}
