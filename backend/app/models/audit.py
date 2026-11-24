import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text
from app.core.db import Base

class AuditLog(Base):
    """
    Append-only audit trail (FR-13, BR-07).
    Records user, action, target entity, before/after states, and reasons.
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String(36), nullable=True)  # User UUID or 'system'
    actor_name = Column(String(120), nullable=True)
    actor_role = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)  # import, assign, status_change, risk_override, comment, approve_user
    entity_type = Column(String(50), nullable=False)  # hotspot, accident_record, import_batch, user
    entity_id = Column(String(36), nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
