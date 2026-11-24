from typing import Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, require_roles, record_audit
from app.core.security import get_password_hash
from app.models.user import User, UserStatusEnum, UserRoleEnum
from app.schemas.user import UserOut, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN])),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status: pending, active, deactivated"),
    search: Optional[str] = Query(None, description="Search by name or email"),
) -> Any:
    """
    List all platform users with filtering (Admin only - FR-01, BR-05).
    """
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter((User.full_name.ilike(s)) | (User.email.ilike(s)))

    return query.order_by(User.created_at.desc()).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN])),
) -> Any:
    """
    Admin explicitly creates an authorized department user.
    """
    normalized_email = user_in.email.strip().lower()
    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    user = User(
        full_name=user_in.full_name.strip(),
        email=normalized_email,
        organisation=user_in.organisation.strip(),
        role=user_in.role,
        password_hash=get_password_hash(user_in.password),
        status=user_in.status or UserStatusEnum.ACTIVE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    record_audit(
        db=db,
        action="admin_create_user",
        entity_type="user",
        entity_id=user.id,
        actor=current_user,
        after_state={"email": user.email, "role": user.role, "status": user.status},
        reason="Direct admin creation",
    )

    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN])),
) -> Any:
    """
    Update user role, organisation, full_name, or status (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    before_state = {
        "full_name": user.full_name,
        "organisation": user.organisation,
        "role": user.role,
        "status": user.status,
    }

    if user_in.full_name is not None:
        user.full_name = user_in.full_name.strip()
    if user_in.organisation is not None:
        user.organisation = user_in.organisation.strip()
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.status is not None:
        user.status = user_in.status

    db.commit()
    db.refresh(user)

    record_audit(
        db=db,
        action="admin_update_user",
        entity_type="user",
        entity_id=user.id,
        actor=current_user,
        before_state=before_state,
        after_state={"role": user.role, "status": user.status},
        reason="Admin user modification",
    )

    return user


@router.post("/{user_id}/approve", response_model=UserOut)
def approve_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN])),
) -> Any:
    """
    Approve a pending user registration (Admin only - FR-01).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = UserStatusEnum.ACTIVE
    db.commit()
    db.refresh(user)

    record_audit(
        db=db,
        action="approve_user",
        entity_type="user",
        entity_id=user.id,
        actor=current_user,
        after_state={"status": user.status},
        reason="Account approved by administrator",
    )

    return user


@router.post("/{user_id}/reject")
def reject_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN])),
) -> Any:
    """
    Reject and delete a pending user registration (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record_audit(
        db=db,
        action="reject_user",
        entity_type="user",
        entity_id=user.id,
        actor=current_user,
        before_state={"email": user.email, "status": user.status},
        reason="Account registration rejected",
    )

    db.delete(user)
    db.commit()
    return {"message": "Account registration rejected and removed"}


@router.post("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.ADMIN])),
) -> Any:
    """
    Deactivate a user account (Admin only - FR-01).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = UserStatusEnum.DEACTIVATED
    db.commit()
    db.refresh(user)

    record_audit(
        db=db,
        action="deactivate_user",
        entity_type="user",
        entity_id=user.id,
        actor=current_user,
        after_state={"status": user.status},
        reason="Account deactivated by administrator",
    )

    return user
