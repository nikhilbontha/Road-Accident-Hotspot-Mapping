import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.db import Base

# Association table between Hotspot and AccidentRecord
hotspot_accidents = Table(
    "hotspot_accidents",
    Base.metadata,
    Column("hotspot_id", String(36), ForeignKey("hotspots.id"), primary_key=True),
    Column("accident_id", String(36), ForeignKey("accident_records.id"), primary_key=True),
)

class Hotspot(Base):
    __tablename__ = "hotspots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, index=True, nullable=False)  # e.g. H-0142
    name = Column(String(255), nullable=False)
    road_name = Column(String(255), nullable=True)
    area = Column(String(100), default="Central")
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    boundary_geojson = Column(JSON, nullable=True)
    accidents_count = Column(Integer, default=0)
    fatalities = Column(Integer, default=0)
    injured = Column(Integer, default=0)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    risk_score = Column(Float, default=0.0)
    score_breakdown = Column(JSON, default=lambda: {"deaths": 0, "frequency": 0, "injuries": 0})
    risk_level = Column(String(20), default="low")  # critical, high, medium, low
    risk_overridden = Column(Boolean, default=False)
    status = Column(String(50), default="Identified")  # Identified, Under review, Assigned, Action in progress, Implemented, Closed
    assignee_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    peak_time_text = Column(String(100), nullable=True)
    analysis_run_id = Column(String(36), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    assignee = relationship("User", back_populates="assigned_hotspots", foreign_keys=[assignee_id])
    accidents = relationship("AccidentRecord", secondary=hotspot_accidents)
    factors = relationship("HotspotFactor", back_populates="hotspot", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="hotspot", cascade="all, delete-orphan")
    comments = relationship("HotspotComment", back_populates="hotspot", cascade="all, delete-orphan")
    interventions = relationship("HotspotIntervention", back_populates="hotspot", cascade="all, delete-orphan")

class HotspotFactor(Base):
    __tablename__ = "hotspot_factors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hotspot_id = Column(String(36), ForeignKey("hotspots.id"), nullable=False)
    factor_key = Column(String(50), nullable=False)
    label = Column(String(100), nullable=False)
    count = Column(Integer, default=0)
    percent = Column(Float, default=0.0)
    time_blocks = Column(JSON, nullable=True)  # 8 bins of 3 hours

    hotspot = relationship("Hotspot", back_populates="factors")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hotspot_id = Column(String(36), ForeignKey("hotspots.id"), nullable=False)
    title = Column(String(255), nullable=False)
    linked_factor = Column(String(100), nullable=False)
    evidence_text = Column(Text, nullable=False)
    confidence = Column(String(20), default="medium")  # high, medium, low
    is_ai_generated = Column(Boolean, default=True)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    hotspot = relationship("Hotspot", back_populates="recommendations")

class HotspotComment(Base):
    __tablename__ = "hotspot_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hotspot_id = Column(String(36), ForeignKey("hotspots.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    hotspot = relationship("Hotspot", back_populates="comments")
    user = relationship("User", back_populates="comments")

class HotspotIntervention(Base):
    __tablename__ = "hotspot_interventions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hotspot_id = Column(String(36), ForeignKey("hotspots.id"), nullable=False)
    description = Column(Text, nullable=False)
    implemented_on = Column(DateTime(timezone=True), nullable=False)
    recorded_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    hotspot = relationship("Hotspot", back_populates="interventions")
