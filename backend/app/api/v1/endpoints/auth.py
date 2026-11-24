from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_active_user, record_audit
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User, UserStatusEnum
from app.schemas.user import UserRegister, UserLogin, UserOut
from app.schemas.token import Token, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserRegister,
    db: Session = Depends(get_db),
) -> Any:
    """
    Register a new department user.
    New accounts start in 'pending' status until approved by an administrator (FR-01, BR-05).
    """
    normalized_email = user_in.email.strip().lower()
    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this work email already exists.",
        )

    user = User(
        full_name=user_in.full_name.strip(),
        email=normalized_email,
        organisation=user_in.organisation.strip(),
        role=user_in.role,
        password_hash=get_password_hash(user_in.password),
        status=UserStatusEnum.PENDING,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    record_audit(
        db=db,
        action="user_register",
        entity_type="user",
        entity_id=user.id,
        actor=user,
        after_state={"email": user.email, "role": user.role, "status": user.status},
        reason="Self-registration via signup form",
    )

    return {
        "message": "Account created. An administrator approves new accounts before you can sign in.",
        "status": user.status,
        "email": user.email,
        "id": user.id,
    }


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
) -> Any:
    """
    Login endpoint with email and password.
    Enforces active status: pending accounts receive clear approval message (FR-01).
    """
    normalized_email = login_data.email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status == UserStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is waiting for approval",
        )

    if user.status == UserStatusEnum.DEACTIVATED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator.",
        )

    user.last_active_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh", response_model=dict)
def refresh_token(
    refresh_req: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Refresh access token using valid refresh token.
    """
    payload = decode_token(refresh_req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.status != UserStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or does not exist",
        )

    new_access_token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current logged in user profile.
    """
    return current_user


@router.post("/logout")
def logout() -> Any:
    """
    Logout endpoint (clears client sessions).
    """
    return {"message": "Successfully logged out"}
