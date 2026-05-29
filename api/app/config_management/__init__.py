"""Configuration management models — DB-driven grow type configs, task templates, overrides."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ─── Grow Type Configuration ───────────────────────────────────────────────────


class GrowTypeProfile(Base):
    __tablename__ = "grow_type_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sensor_kit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_context_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    extended_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    stages: Mapped[list[GrowTypeStage]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    equipment: Mapped[list[GrowTypeEquipment]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    troubleshooting: Mapped[list[GrowTypeTroubleshooting]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class GrowTypeStage(Base):
    __tablename__ = "grow_type_stages"
    __table_args__ = (UniqueConstraint("profile_id", "slug", name="uq_grow_type_stage_profile_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_type_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_days_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_days_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)

    profile: Mapped[GrowTypeProfile] = relationship(back_populates="stages")
    environment: Mapped[GrowTypeEnvironment | None] = relationship(
        back_populates="stage", uselist=False, cascade="all, delete-orphan"
    )
    nutrients: Mapped[list[GrowTypeNutrient]] = relationship(back_populates="stage", cascade="all, delete-orphan")
    watering: Mapped[GrowTypeWatering | None] = relationship(
        back_populates="stage", uselist=False, cascade="all, delete-orphan"
    )


class GrowTypeEnvironment(Base):
    __tablename__ = "grow_type_environment"
    __table_args__ = (UniqueConstraint("stage_id", name="uq_grow_type_environment_stage"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_type_stages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    temp_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_ideal: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_ideal: Mapped[float | None] = mapped_column(Float, nullable=True)
    vpd_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    vpd_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    light_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    light_ppfd_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    light_ppfd_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    co2_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    co2_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_temp_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_temp_max: Mapped[float | None] = mapped_column(Float, nullable=True)

    stage: Mapped[GrowTypeStage] = relationship(back_populates="environment")


class GrowTypeNutrient(Base):
    __tablename__ = "grow_type_nutrients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_type_stages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ec_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    ec_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    ec_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    ph_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    base_nutrients: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    supplements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    stage: Mapped[GrowTypeStage] = relationship(back_populates="nutrients")


class GrowTypeWatering(Base):
    __tablename__ = "grow_type_watering"
    __table_args__ = (UniqueConstraint("stage_id", name="uq_grow_type_watering_stage"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_type_stages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_ml: Mapped[float | None] = mapped_column(Float, nullable=True)
    runoff_target_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    stage: Mapped[GrowTypeStage] = relationship(back_populates="watering")


class GrowTypeEquipment(Base):
    __tablename__ = "grow_type_equipment"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_type_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchase_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    profile: Mapped[GrowTypeProfile] = relationship(back_populates="equipment")


class GrowTypeTroubleshooting(Base):
    __tablename__ = "grow_type_troubleshooting"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_type_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_type_stages.id", ondelete="SET NULL"), nullable=True
    )
    symptom: Mapped[str] = mapped_column(Text, nullable=False)
    cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    profile: Mapped[GrowTypeProfile] = relationship(back_populates="troubleshooting")


# ─── Task Templates ────────────────────────────────────────────────────────────


class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    grow_type_slugs: Mapped[list | None] = mapped_column(ARRAY(String(100)), nullable=True)
    frequency_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    stage_slug: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    routine: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    steps: Mapped[list[TaskTemplateStep]] = relationship(back_populates="template", cascade="all, delete-orphan")


class TaskTemplateStep(Base):
    __tablename__ = "task_template_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    optional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    template: Mapped[TaskTemplate] = relationship(back_populates="steps")


# ─── Tenant Config Overrides ──────────────────────────────────────────────────


class TenantConfigOverride(Base):
    __tablename__ = "tenant_config_overrides"
    __table_args__ = (UniqueConstraint("tenant_id", "config_type", "config_key", name="uq_tenant_config_override"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    config_type: Mapped[str] = mapped_column(String(50), nullable=False)
    config_key: Mapped[str] = mapped_column(String(500), nullable=False)
    override_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
