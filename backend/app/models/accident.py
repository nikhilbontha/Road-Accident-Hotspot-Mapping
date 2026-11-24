import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    object_key = Column(String(500), nullable=True)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    template_version = Column(String(20), default="v2")
    total_rows = Column(Integer, default=0)
    accepted_rows = Column(Integer, default=0)
    corrected_rows = Column(Integer, default=0)
    rejected_rows = Column(Integer, default=0)
    masked_counts = Column(JSON, default=lambda: {"vehicle_numbers": 0, "names": 0, "phone_numbers": 0})
    status = Column(String(20), default="uploaded")  # uploaded, checked, reviewed, imported, failed
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    issues = relationship("ImportIssue", back_populates="batch", cascade="all, delete-orphan")
    records = relationship("AccidentRecord", back_populates="batch")

class ImportIssue(Base):
    __tablename__ = "import_issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("import_batches.id"), nullable=False)
    row_number = Column(Integer, nullable=False)
    issue_type = Column(String(100), nullable=False)  # invalid_coordinate, duplicate, address_only, typo, missing_field
    field = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    action = Column(String(20), default="fix")  # fix, skip, accept, done
    resolved = Column(Boolean, default=False)

    batch = relationship("ImportBatch", back_populates="issues")

class AccidentRecord(Base):
    __tablename__ = "accident_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    accident_code = Column(String(50), unique=True, index=True, nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_text = Column(String(255), nullable=False)
    geocode_confidence = Column(Float, default=1.0)
    road_name = Column(String(255), nullable=True)
    road_type = Column(String(50), default="city_road")  # national_highway, city_road, junction, other
    severity = Column(String(50), nullable=False)  # fatal, grievous_injury, minor_injury, non_injury
    fatalities = Column(Integer, default=0)
    injuries = Column(Integer, default=0)
    vehicle_types = Column(JSON, default=list)
    weather = Column(String(50), default="Clear")
    light_condition = Column(String(50), default="Daylight")
    probable_cause = Column(String(255), nullable=True)
    source_batch_id = Column(String(36), ForeignKey("import_batches.id"), nullable=True)
    flags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    batch = relationship("ImportBatch", back_populates="records")
