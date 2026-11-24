import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.db import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # critical_detected, assigned, risk_changed, action_implemented
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    entity_id = Column(String(36), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="notifications")

class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    critical_detected = Column(Boolean, default=True)
    assigned = Column(Boolean, default=True)
    risk_changed = Column(Boolean, default=True)
    action_implemented = Column(Boolean, default=True)

    user = relationship("User", back_populates="notification_settings")
