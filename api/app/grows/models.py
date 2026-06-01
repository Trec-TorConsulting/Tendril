"""Grow feature models — tents, grow cycles, buckets, sensors, journals, etc."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ---------- Tents ----------


class Tent(Base):
    __tablename__ = "tents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    environment_type: Mapped[str] = mapped_column(String(50), default="indoor")  # indoor | outdoor | greenhouse
    size: Mapped[str | None] = mapped_column(String(50))  # e.g. "4x4", "3x3", "5x5x8"
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    camera_url: Mapped[str | None] = mapped_column(String(1024))  # DEPRECATED: use tent_cameras table
    equipment: Mapped[list | None] = mapped_column(JSON, default=list)  # list of equipment objects
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    grow_cycles: Mapped[list[GrowCycle]] = relationship(back_populates="tent", cascade="all, delete-orphan")
    ambient_readings: Mapped[list[TentSensorReading]] = relationship(
        back_populates="tent", cascade="all, delete-orphan"
    )
    cameras: Mapped[list[TentCamera]] = relationship(
        back_populates="tent", cascade="all, delete-orphan", order_by="TentCamera.sort_order"
    )


class TentCamera(Base):
    __tablename__ = "tent_cameras"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String(100), nullable=False, default="Camera")
    camera_type: Mapped[str] = mapped_column(String(20), nullable=False, default="http_snapshot")
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    tent: Mapped[Tent] = relationship(back_populates="cameras")


# ---------- Grow Cycles ----------


class GrowCycle(Base):
    __tablename__ = "grow_cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    tent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tents.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grow_type: Mapped[str] = mapped_column(String(50), nullable=False)  # dwc, rdwc, nft, etc.
    status: Mapped[str] = mapped_column(String(50), default="active")  # active | harvesting | completed | archived
    stage: Mapped[str] = mapped_column(
        String(50), default="seedling"
    )  # seedling | vegetative | flowering | ripening | harvesting | drying | curing
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    milestones: Mapped[dict | None] = mapped_column(JSON)  # {stage: iso-datetime}
    # Grow-type-specific settings stored as JSON
    settings: Mapped[dict | None] = mapped_column(JSON)
    auto_health_check: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    cached_feeding_advice: Mapped[dict | None] = mapped_column(JSON)
    feeding_advice_cached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    tent: Mapped[Tent] = relationship(back_populates="grow_cycles")
    buckets: Mapped[list[Bucket]] = relationship(back_populates="grow_cycle", cascade="all, delete-orphan")
    grow_photos: Mapped[list[GrowPhoto]] = relationship(back_populates="grow_cycle", cascade="all, delete-orphan")


# ---------- Buckets ----------


class Bucket(Base):
    __tablename__ = "buckets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, default=1)
    label: Mapped[str | None] = mapped_column(String(255))
    strain_name: Mapped[str | None] = mapped_column(String(255))
    strain_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("strains.id", ondelete="SET NULL"), nullable=True
    )
    growth_stage: Mapped[str] = mapped_column(String(50), default="seedling")
    status: Mapped[str] = mapped_column(String(50), default="active")  # active | harvested | removed
    volume_gallons: Mapped[float | None] = mapped_column(Float)
    role: Mapped[str] = mapped_column(String(20), default="site")  # site | header
    # Grow-type-specific fields stored as JSON
    settings: Mapped[dict | None] = mapped_column(JSON)
    # Outdoor grid placement
    grid_row: Mapped[int | None] = mapped_column(Integer)
    grid_col: Mapped[int | None] = mapped_column(Integer)
    plant_spacing_in: Mapped[int | None] = mapped_column(Integer)
    companion_plants: Mapped[list | None] = mapped_column(JSON)
    sun_zone: Mapped[str | None] = mapped_column(String(50))
    planting_method: Mapped[str | None] = mapped_column(String(50))  # direct_seed | transplant | clone
    transplant_date: Mapped[datetime | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    grow_cycle: Mapped[GrowCycle] = relationship(back_populates="buckets")
    strain: Mapped[Strain | None] = relationship(lazy="joined")
    sensor_readings: Mapped[list[BucketSensorReading]] = relationship(
        back_populates="bucket", cascade="all, delete-orphan"
    )
    journal_entries: Mapped[list[JournalEntry]] = relationship(back_populates="bucket", cascade="all, delete-orphan")
    photos: Mapped[list[BucketPhoto]] = relationship(back_populates="bucket", cascade="all, delete-orphan")


# ---------- Sensor Readings ----------


class BucketSensorReading(Base):
    __tablename__ = "bucket_sensor_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[str | None] = mapped_column(String(100))

    # Core hydro sensors
    water_temp_f: Mapped[float | None] = mapped_column(Float)
    ph: Mapped[float | None] = mapped_column(Float)
    ec: Mapped[float | None] = mapped_column(Float)
    ppm: Mapped[float | None] = mapped_column(Float)
    water_level_pct: Mapped[float | None] = mapped_column(Float)
    dissolved_oxygen: Mapped[float | None] = mapped_column(Float)
    orp: Mapped[float | None] = mapped_column(Float)  # Oxidation Reduction Potential (mV)
    salinity: Mapped[float | None] = mapped_column(Float)  # ppt
    specific_gravity: Mapped[float | None] = mapped_column(Float)  # S.G.

    # Device status
    battery_pct: Mapped[float | None] = mapped_column(Float)

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

    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    bucket: Mapped[Bucket] = relationship(back_populates="sensor_readings")


# ---------- Journal Entries ----------


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # note | feeding | water_change | training | transplant | defoliation | topping | etc.
    content: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSON)  # structured data (e.g., nutrients used, amounts)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    bucket: Mapped[Bucket] = relationship(back_populates="journal_entries")


# ---------- Bucket Photos ----------


class BucketPhoto(Base):
    __tablename__ = "bucket_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    caption: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    bucket: Mapped[Bucket] = relationship(back_populates="photos")


# ---------- Grow Photos (grow-level, supports file uploads & health-check snapshots) ----------


class GrowPhoto(Base):
    __tablename__ = "grow_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[str] = mapped_column(String(50), default="upload")  # upload | health_check
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)  # S3 object key
    caption: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    grow_cycle: Mapped[GrowCycle] = relationship(back_populates="grow_photos")


# ---------- Dose Profiles ----------


class DoseProfile(Base):
    __tablename__ = "dose_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dose_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ph_up | ph_down | nutrient_a | nutrient_b | calmag | etc.
    dose_ml: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict | None] = mapped_column(JSON)  # thresholds, intervals, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Feeding Schedules ----------


class FeedingSchedule(Base):
    __tablename__ = "feeding_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)  # seedling | vegetative | flowering | etc.
    nutrients: Mapped[dict] = mapped_column(JSON, nullable=False)  # [{name, brand, ml_per_gallon, strength_pct}]
    target_ppm: Mapped[float | None] = mapped_column(Float)
    target_ec: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Strains ----------


class Strain(Base):
    __tablename__ = "strains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    breeder: Mapped[str | None] = mapped_column(String(255))
    genetics: Mapped[str | None] = mapped_column(String(255))  # e.g., "indica/sativa hybrid"
    flowering_days: Mapped[int | None] = mapped_column(Integer)
    thc_pct: Mapped[float | None] = mapped_column(Float)
    cbd_pct: Mapped[float | None] = mapped_column(Float)
    terpene_profile: Mapped[dict | None] = mapped_column(JSON)  # [{name, pct}]
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Yields ----------


class Yield(Base):
    __tablename__ = "yields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
    )
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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Weather Readings ----------


class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    tent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tents.id", ondelete="CASCADE"), nullable=False
    )
    temperature_c: Mapped[float | None] = mapped_column(Float)
    humidity_pct: Mapped[float | None] = mapped_column(Float)
    precipitation_mm: Mapped[float | None] = mapped_column(Float)
    wind_speed_kmh: Mapped[float | None] = mapped_column(Float)
    uv_index: Mapped[float | None] = mapped_column(Float)
    weather_code: Mapped[int | None] = mapped_column(Integer)
    forecast: Mapped[dict | None] = mapped_column(JSON)  # 7-day forecast data
    dew_point_c: Mapped[float | None] = mapped_column(Float)
    pressure_hpa: Mapped[float | None] = mapped_column(Float)
    soil_temp_c: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str | None] = mapped_column(String(50))  # "open_meteo", "openweather", "ecowitt", "manual"
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Tent Sensor Readings (ambient temp & humidity — one per tent, not per bucket) ----------


class TentSensorReading(Base):
    __tablename__ = "tent_sensor_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    tent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tents.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[str | None] = mapped_column(String(100))
    ambient_temp_f: Mapped[float | None] = mapped_column(Float)
    ambient_humidity: Mapped[float | None] = mapped_column(Float)
    vpd: Mapped[float | None] = mapped_column(Float)
    co2: Mapped[float | None] = mapped_column(Float)
    lux: Mapped[float | None] = mapped_column(Float)
    dew_point_f: Mapped[float | None] = mapped_column(Float)
    par_ppfd: Mapped[float | None] = mapped_column(Float)
    air_pressure: Mapped[float | None] = mapped_column(Float)
    voc: Mapped[float | None] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    tent: Mapped[Tent] = relationship(back_populates="ambient_readings")


# ---------- Grow Type Profiles (migrated to config_management module) ----------
# The GrowTypeProfile model now lives in app.config_management
# Import from there if needed:
# from app.config_management import GrowTypeProfile


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
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


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
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Health Evaluations (Gemini-powered) ----------


class HealthEval(Base):
    __tablename__ = "health_evals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int | None] = mapped_column(Integer)
    issues: Mapped[list | None] = mapped_column(JSON)
    actions: Mapped[list | None] = mapped_column(JSON)
    raw_analysis: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source: Mapped[str] = mapped_column(String(50), default="manual")  # manual | scheduled | diagnose
    diagnosis_treatment_ids: Mapped[list | None] = mapped_column(JSON, default=list)
    confidence_scores: Mapped[dict | None] = mapped_column(JSON, default=dict)
    severity: Mapped[str | None] = mapped_column(String(20))  # low | medium | high | critical
    model_used: Mapped[str | None] = mapped_column(String(100))  # ollama:llava | gemini-2.5-flash
    photo_storage_key: Mapped[str | None] = mapped_column(String(1024))  # S3 key for associated photo
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Plant Health Treatments (reference data) ----------


class PlantHealthTreatment(Base):
    __tablename__ = "plant_health_treatments"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g., "nitrogen_deficiency"
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    aka: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    symptoms: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    identification_tips: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    causes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    severity_criteria: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    treatments: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    prevention: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    recovery_time: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    commonly_confused_with: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Plot Grids (outdoor soil garden layout) ----------


class PlotGrid(Base):
    __tablename__ = "plot_grids"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    rows: Mapped[int] = mapped_column(Integer, nullable=False)
    cols: Mapped[int] = mapped_column(Integer, nullable=False)
    cell_size_inches: Mapped[int] = mapped_column(Integer, default=12)
    orientation: Mapped[str] = mapped_column(String(10), default="north")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    cells: Mapped[list[PlotCell]] = relationship(back_populates="grid", cascade="all, delete-orphan")


class PlotCell(Base):
    __tablename__ = "plot_cells"
    __table_args__ = (UniqueConstraint("plot_grid_id", "row", "col", name="uq_plot_cell_position"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    plot_grid_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plot_grids.id", ondelete="CASCADE"), nullable=False
    )
    row: Mapped[int] = mapped_column(Integer, nullable=False)
    col: Mapped[int] = mapped_column(Integer, nullable=False)
    cell_type: Mapped[str] = mapped_column(
        String(50), default="empty"
    )  # plant | companion | path | empty | sensor | irrigation
    bucket_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="SET NULL"), nullable=True
    )
    companion_plant: Mapped[str | None] = mapped_column(String(100))
    device_id: Mapped[str | None] = mapped_column(String(100))
    irrigation_zone: Mapped[str | None] = mapped_column(String(100))
    sun_zone: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    grid: Mapped[PlotGrid] = relationship(back_populates="cells")


# ---------- Soil Tests ----------


class SoilTest(Base):
    __tablename__ = "soil_tests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    tested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    ph: Mapped[float | None] = mapped_column(Float)
    nitrogen_ppm: Mapped[float | None] = mapped_column(Float)
    phosphorus_ppm: Mapped[float | None] = mapped_column(Float)
    potassium_ppm: Mapped[float | None] = mapped_column(Float)
    organic_matter_pct: Mapped[float | None] = mapped_column(Float)
    cec: Mapped[float | None] = mapped_column(Float)
    calcium_ppm: Mapped[float | None] = mapped_column(Float)
    magnesium_ppm: Mapped[float | None] = mapped_column(Float)
    sulfur_ppm: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(50), default="home_kit")  # lab | home_kit | sensor
    notes: Mapped[str | None] = mapped_column(Text)


# ---------- Soil Amendments ----------


class SoilAmendment(Base):
    __tablename__ = "soil_amendments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    amendment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[str | None] = mapped_column(String(255))
    area_applied: Mapped[str | None] = mapped_column(String(255))
    cost: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)


# ---------- Pest Scout Entries ----------


class PestScoutEntry(Base):
    __tablename__ = "pest_scout_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    scouted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    pest_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # insect | disease | animal | beneficial | unknown
    species: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="low")  # low | medium | high | critical
    grid_row: Mapped[int | None] = mapped_column(Integer)
    grid_col: Mapped[int | None] = mapped_column(Integer)
    photo_url: Mapped[str | None] = mapped_column(String(1024))
    treatment_applied: Mapped[str | None] = mapped_column(String(255))
    treatment_type: Mapped[str | None] = mapped_column(String(50))  # organic | synthetic | biological | physical | none
    notes: Mapped[str | None] = mapped_column(Text)


# ---------- Harvest Yields (per-plant outdoor tracking) ----------


class HarvestYield(Base):
    __tablename__ = "harvest_yields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
    )
    harvested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    wet_weight_oz: Mapped[float | None] = mapped_column(Float)
    dry_weight_oz: Mapped[float | None] = mapped_column(Float)
    trim_weight_oz: Mapped[float | None] = mapped_column(Float)
    quality_rating: Mapped[int | None] = mapped_column(Integer)  # 1-10
    trichome_stage: Mapped[str | None] = mapped_column(String(50))  # clear | cloudy | amber | mixed
    notes: Mapped[str | None] = mapped_column(Text)


# ---------- Container Profiles (outdoor container grow metadata) ----------


class ContainerProfile(Base):
    __tablename__ = "container_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    pot_size_gallons: Mapped[float | None] = mapped_column(Float)
    media_type: Mapped[str | None] = mapped_column(String(100))
    pot_color: Mapped[str | None] = mapped_column(String(50))
    pot_material: Mapped[str | None] = mapped_column(String(50))
    has_saucer: Mapped[bool] = mapped_column(Boolean, default=False)
    is_mobile: Mapped[bool] = mapped_column(Boolean, default=True)
    sun_exposure: Mapped[str | None] = mapped_column(String(50))
    location_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Runoff Readings (input vs runoff pH/EC tracking) ----------


class RunoffReading(Base):
    __tablename__ = "runoff_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
    )
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    input_ph: Mapped[float | None] = mapped_column(Float)
    input_ec: Mapped[float | None] = mapped_column(Float)
    runoff_ph: Mapped[float | None] = mapped_column(Float)
    runoff_ec: Mapped[float | None] = mapped_column(Float)
    runoff_pct: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
