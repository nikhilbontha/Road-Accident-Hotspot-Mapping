from typing import Generator, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import decode_token
from app.models.user import User, UserStatusEnum
from app.models.audit import AuditLog

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.status == UserStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is waiting for approval",
        )
    if current_user.status == UserStatusEnum.DEACTIVATED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator.",
        )
    return current_user


def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{current_user.role}'. Required: {allowed_roles}",
            )
        return current_user
    return role_checker


def record_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    actor: Optional[User] = None,
    before_state: Optional[dict] = None,
    after_state: Optional[dict] = None,
    reason: Optional[str] = None,
):
    """
    Append an immutable log entry to audit_logs (BR-07, FR-13).
    """
    log = AuditLog(
        actor_id=actor.id if actor else None,
        actor_name=actor.full_name if actor else "System",
        actor_role=actor.role if actor else "system",
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        before_state=before_state,
        after_state=after_state,
        reason=reason,
    )
    db.add(log)
    db.commit()
