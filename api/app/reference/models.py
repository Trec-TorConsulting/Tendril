"""Reference data models — DB-backed replacements for hardcoded config."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StageTransitionTask(Base):
    __tablename__ = "stage_transition_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    brief: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    routine: Mapped[str] = mapped_column(String(30), nullable=False, default="on_demand")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    grow_type_slugs: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class AutomationSuppression(Base):
    __tablename__ = "automation_suppressions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    automation_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    suppressed_categories: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    verify_task: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class CompanionPlant(Base):
    __tablename__ = "companion_plants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    benefits: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    companions: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    antagonists: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    spacing_inches: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class FeedChart(Base):
    __tablename__ = "feed_charts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    line: Mapped[str] = mapped_column(String(100), nullable=False)
    medium: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    products: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    schedule: Mapped[dict] = mapped_column(JSON, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class NutrientKnowledge(Base):
    __tablename__ = "nutrient_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ESPHomeTemplate(Base):
    __tablename__ = "esphome_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sensors: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    board: Mapped[str] = mapped_column(String(50), nullable=False, default="esp32dev")
    yaml_body: Mapped[str] = mapped_column(Text, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
