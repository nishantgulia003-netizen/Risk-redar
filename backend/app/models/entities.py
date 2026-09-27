"""PostGIS-backed persistence models for RiskRadar's district datasets."""
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Area(Base):
    __tablename__ = "areas"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    geometry: Mapped[WKBElement] = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    elderly_pct: Mapped[float] = mapped_column(Float, nullable=False)
    children_pct: Mapped[float] = mapped_column(Float, nullable=False)
    historical_disaster_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hazards: Mapped[list["HazardLayer"]] = relationship(back_populates="area", cascade="all, delete-orphan")

class HazardLayer(Base):
    __tablename__ = "hazard_layers"
    __table_args__ = (CheckConstraint("hazard_type IN ('flood', 'landslide', 'rainfall')", name="ck_hazard_type"), CheckConstraint("intensity >= 0 AND intensity <= 1", name="ck_hazard_intensity"))
    id: Mapped[int] = mapped_column(primary_key=True)
    area_id: Mapped[int | None] = mapped_column(ForeignKey("areas.id", ondelete="SET NULL"), index=True)
    hazard_type: Mapped[str] = mapped_column(String(30), nullable=False)
    intensity: Mapped[float] = mapped_column(Float, nullable=False)
    geometry: Mapped[WKBElement] = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)
    area: Mapped[Area | None] = relationship(back_populates="hazards")

class Shelter(Base):
    __tablename__ = "shelters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    geometry: Mapped[WKBElement] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    medical_facility: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    water_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    road_accessible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class RoadSegment(Base):
    __tablename__ = "road_segments"
    id: Mapped[int] = mapped_column(primary_key=True)
    geometry: Mapped[WKBElement] = mapped_column(Geometry("LINESTRING", srid=4326), nullable=False)
    passes_hazard_zone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    length_km: Mapped[float] = mapped_column(Float, nullable=False)


class SafetyReport(Base):
    """An observed safety condition; target_id is polymorphic by target_type."""
    __tablename__ = "safety_reports"
    __table_args__ = (
        CheckConstraint("target_type IN ('road_segment', 'shelter', 'area')", name="ck_safety_report_target_type"),
        CheckConstraint("source_type IN ('police', 'rescue_team', 'news', 'user')", name="ck_safety_report_source_type"),
        CheckConstraint("status IN ('unsafe', 'safe', 'blocked', 'clear')", name="ck_safety_report_status"),
        Index("ix_safety_reports_target_created", "target_type", "target_id", "created_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Deliberately not a physical FK: this can reference any of three tables.
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reporter_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
