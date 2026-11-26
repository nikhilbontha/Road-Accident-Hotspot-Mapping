import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text, event, DDL
from app.core.db import Base

class AuditLog(Base):
    """
    Append-only audit trail (FR-13, BR-07).
    Records user, action, target entity, before/after states, and reasons.
    Updates and Deletes are prohibited by database trigger and ORM guards.
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

# SQLite trigger to block UPDATE and DELETE at the SQL engine level
audit_log_no_update_sql = """
CREATE TRIGGER IF NOT EXISTS audit_logs_prevent_update
BEFORE UPDATE ON audit_logs
BEGIN
    SELECT RAISE(ABORT, 'audit_logs is append-only: updates are prohibited');
END;
"""

audit_log_no_delete_sql = """
CREATE TRIGGER IF NOT EXISTS audit_logs_prevent_delete
BEFORE DELETE ON audit_logs
BEGIN
    SELECT RAISE(ABORT, 'audit_logs is append-only: deletes are prohibited');
END;
"""

event.listen(AuditLog.__table__, 'after_create', DDL(audit_log_no_update_sql))
event.listen(AuditLog.__table__, 'after_create', DDL(audit_log_no_delete_sql))

@event.listens_for(AuditLog, 'before_update')
def receive_before_update(mapper, connection, target):
    raise PermissionError("audit_logs is append-only: updates are prohibited (FR-13b)")

@event.listens_for(AuditLog, 'before_delete')
def receive_before_delete(mapper, connection, target):
    raise PermissionError("audit_logs is append-only: deletes are prohibited (FR-13b)")
