import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.db import Base

class UserRoleEnum(str):
    ADMIN = "admin"
    POLICE_OFFICER = "police_officer"
    SAFETY_ANALYST = "safety_analyst"
    AUTHORITY_OFFICIAL = "authority_official"
    PUBLIC_VIEWER = "public_viewer"

class UserStatusEnum(str):
    PENDING = "pending"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    organisation = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRoleEnum.SAFETY_ANALYST)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default=UserStatusEnum.PENDING)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships with cascade delete-orphan
    assigned_hotspots = relationship("Hotspot", back_populates="assignee", foreign_keys="Hotspot.assignee_id")
    comments = relationship("HotspotComment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    notification_settings = relationship("NotificationSetting", back_populates="user", uselist=False, cascade="all, delete-orphan")
