"""Grow feature models — tents, grow cycles, buckets, sensors, journals, etc."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------- Tents ----------

class Tent(Base):
    __tablename__ = "tents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    environment_type: Mapped[str] = mapped_column(String(50), default="indoor")  # indoor | outdoor | greenhouse
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    camera_url: Mapped[str | None] = mapped_column(String(1024))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    grow_cycles: Mapped[list[GrowCycle]] = relationship(back_populates="tent", cascade="all, delete-orphan")


# ---------- Grow Cycles ----------

class GrowCycle(Base):
    __tablename__ = "grow_cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tents.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grow_type: Mapped[str] = mapped_column(String(50), nullable=False)  # dwc, rdwc, nft, etc.
    status: Mapped[str] = mapped_column(String(50), default="active")  # active | harvesting | completed | archived
    stage: Mapped[str] = mapped_column(String(50), default="seedling")  # seedling | vegetative | flowering | ripening | harvesting | drying | curing
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    milestones: Mapped[dict | None] = mapped_column(JSON)  # {stage: iso-datetime}
    # Grow-type-specific settings stored as JSON
    settings: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tent: Mapped[Tent] = relationship(back_populates="grow_cycles")
    buckets: Mapped[list[Bucket]] = relationship(back_populates="grow_cycle", cascade="all, delete-orphan")


# ---------- Buckets ----------

class Bucket(Base):
    __tablename__ = "buckets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=1)
    label: Mapped[str | None] = mapped_column(String(255))
    strain_name: Mapped[str | None] = mapped_column(String(255))
    growth_stage: Mapped[str] = mapped_column(String(50), default="seedling")
    status: Mapped[str] = mapped_column(String(50), default="active")  # active | harvested | removed
    volume_gallons: Mapped[float | None] = mapped_column(Float)
    # Grow-type-specific fields stored as JSON
    settings: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    grow_cycle: Mapped[GrowCycle] = relationship(back_populates="buckets")
    sensor_readings: Mapped[list[BucketSensorReading]] = relationship(back_populates="bucket", cascade="all, delete-orphan")
    journal_entries: Mapped[list[JournalEntry]] = relationship(back_populates="bucket", cascade="all, delete-orphan")
    photos: Mapped[list[BucketPhoto]] = relationship(back_populates="bucket", cascade="all, delete-orphan")


# ---------- Sensor Readings ----------

class BucketSensorReading(Base):
    __tablename__ = "bucket_sensor_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(100))

    # Core hydro sensors
    water_temp_f: Mapped[float | None] = mapped_column(Float)
    ph: Mapped[float | None] = mapped_column(Float)
    ec: Mapped[float | None] = mapped_column(Float)
    ppm: Mapped[float | None] = mapped_column(Float)
    water_level_pct: Mapped[float | None] = mapped_column(Float)
    dissolved_oxygen: Mapped[float | None] = mapped_column(Float)

    # Flow / pressure sensors
    flow_rate: Mapped[float | None] = mapped_column(Float)
    mist_pressure: Mapped[float | None] = mapped_column(Float)

    # Soil / media sensors
    soil_moisture: Mapped[float | None] = mapped_column(Float)
    soil_temp: Mapped[float | None] = mapped_column(Float)

    # Runoff sensors
    runoff_ph: Mapped[float | None] = mapped_column(Float)
    runoff_ec: Mapped[float | None] = mapped_column(Float)

    # Ambient environment
    ambient_temp_f: Mapped[float | None] = mapped_column(Float)
    ambient_humidity: Mapped[float | None] = mapped_column(Float)

    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    bucket: Mapped[Bucket] = relationship(back_populates="sensor_readings")


# ---------- Journal Entries ----------

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # note | feeding | water_change | training | transplant | defoliation | topping | etc.
    content: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSON)  # structured data (e.g., nutrients used, amounts)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    bucket: Mapped[Bucket] = relationship(back_populates="journal_entries")


# ---------- Bucket Photos ----------

class BucketPhoto(Base):
    __tablename__ = "bucket_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    caption: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    bucket: Mapped[Bucket] = relationship(back_populates="photos")


# ---------- Dose Profiles ----------

class DoseProfile(Base):
    __tablename__ = "dose_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dose_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ph_up | ph_down | nutrient_a | nutrient_b | calmag | etc.
    dose_ml: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict | None] = mapped_column(JSON)  # thresholds, intervals, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------- Feeding Schedules ----------

class FeedingSchedule(Base):
    __tablename__ = "feeding_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)  # seedling | vegetative | flowering | etc.
    nutrients: Mapped[dict] = mapped_column(JSON, nullable=False)  # [{name, brand, ml_per_gallon, strength_pct}]
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------- Strains ----------

class Strain(Base):
    __tablename__ = "strains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    breeder: Mapped[str | None] = mapped_column(String(255))
    genetics: Mapped[str | None] = mapped_column(String(255))  # e.g., "indica/sativa hybrid"
    flowering_days: Mapped[int | None] = mapped_column(Integer)
    thc_pct: Mapped[float | None] = mapped_column(Float)
    cbd_pct: Mapped[float | None] = mapped_column(Float)
    terpene_profile: Mapped[dict | None] = mapped_column(JSON)  # [{name, pct}]
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------- Yields ----------

class Yield(Base):
    __tablename__ = "yields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    bucket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False)
    wet_weight_g: Mapped[float | None] = mapped_column(Float)
    dry_weight_g: Mapped[float | None] = mapped_column(Float)
    trim_weight_g: Mapped[float | None] = mapped_column(Float)
    quality_rating: Mapped[int | None] = mapped_column(Integer)  # 1-10
    terpene_notes: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    # Harvest workflow phases
    harvest_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dry_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dry_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cure_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cure_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dry_environment: Mapped[dict | None] = mapped_column(JSON)  # {temp_f, humidity_pct}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------- Weather Readings ----------

class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tents.id", ondelete="CASCADE"), nullable=False)
    temperature_c: Mapped[float | None] = mapped_column(Float)
    humidity_pct: Mapped[float | None] = mapped_column(Float)
    precipitation_mm: Mapped[float | None] = mapped_column(Float)
    wind_speed_kmh: Mapped[float | None] = mapped_column(Float)
    uv_index: Mapped[float | None] = mapped_column(Float)
    weather_code: Mapped[int | None] = mapped_column(Integer)
    forecast: Mapped[dict | None] = mapped_column(JSON)  # 7-day forecast data
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------- Grow Type Profiles (seed data — read-only) ----------

class GrowTypeProfile(Base):
    __tablename__ = "grow_type_profiles"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., "dwc", "nft", "soil"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # hydroponic_active | hydroponic_passive | soilless | traditional | outdoor
    description: Mapped[str] = mapped_column(Text, nullable=False)
    terminology: Mapped[dict] = mapped_column(JSON, nullable=False)
    sensor_kit: Mapped[str] = mapped_column(String(100), nullable=False)
    relevant_sensors: Mapped[list] = mapped_column(JSON, nullable=False)
    primary_sensors: Mapped[list] = mapped_column(JSON, nullable=False)
    irrelevant_sensors: Mapped[list] = mapped_column(JSON, nullable=False)
    unique_fields: Mapped[list] = mapped_column(JSON, nullable=False)
    ph_range: Mapped[dict] = mapped_column(JSON, nullable=False)  # {min, max}
    ec_range: Mapped[dict] = mapped_column(JSON, nullable=False)  # {seedling, veg, flower}
    health_check_questions: Mapped[list] = mapped_column(JSON, nullable=False)
    automations: Mapped[list] = mapped_column(JSON, nullable=False)
    feeding_approach: Mapped[str] = mapped_column(Text, nullable=False)
    nutrient_strength: Mapped[str] = mapped_column(String(50), nullable=False)
    common_problems: Mapped[list] = mapped_column(JSON, nullable=False)
    ai_prompt_context: Mapped[str] = mapped_column(Text, nullable=False)


# ---------- Reference Strains (synced from external API) ----------

class ReferenceStrain(Base):
    __tablename__ = "reference_strains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    breeder: Mapped[str | None] = mapped_column(String(255))
    genetics: Mapped[str | None] = mapped_column(String(255))
    thc_pct: Mapped[float | None] = mapped_column(Float)
    cbd_pct: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------- Nutrient Products (barcode scan) ----------

class NutrientProduct(Base):
    __tablename__ = "nutrient_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    barcode: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255))
    npk: Mapped[str | None] = mapped_column(String(50))  # e.g., "3-1-2"
    nutrients: Mapped[dict | None] = mapped_column(JSON)
    image_url: Mapped[str | None] = mapped_column(String(1024))
    source: Mapped[str] = mapped_column(String(50), default="open_food_facts")
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
