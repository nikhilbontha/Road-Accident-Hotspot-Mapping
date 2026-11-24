import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text
from app.core.db import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_number = Column(String(50), unique=True, nullable=False)
    started_by = Column(String(36), nullable=False)
    parameters = Column(JSON, nullable=False)  # radius_m: 250, min_accidents: 5, weights, etc.
    status = Column(String(20), default="running")  # running, completed, failed
    record_count = Column(String(50), default="0")
    duration_ms = Column(String(50), default="0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # summary, trends, intervention
    params = Column(JSON, nullable=False)
    format = Column(String(10), default="pdf")  # pdf, csv
    object_key = Column(String(500), nullable=True)
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
