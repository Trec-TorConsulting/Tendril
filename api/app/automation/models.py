"""Automation models — rules, schedules, alert history."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    grow_cycle_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("grow_cycles.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sensor: Mapped[str] = mapped_column(String(50), nullable=False)  # ph, ec, water_temp, etc.
    condition: Mapped[str] = mapped_column(String(10), nullable=False)  # gt, lt, gte, lte, eq
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # alert, dose_ph_up, dose_ph_down, notify, etc.
    action_params: Mapped[dict | None] = mapped_column(JSON)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=30)
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # info, warning, critical
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("automation_rules.id"))
    grow_cycle_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("grow_cycles.id"))
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sensor_value: Mapped[float | None] = mapped_column(Float)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EnvironmentSchedule(Base):
    __tablename__ = "environment_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    tent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tents.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # light, fan, hvac, pump
    stage: Mapped[str | None] = mapped_column(String(50))  # vegetative, flowering, etc.
    on_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    off_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    settings: Mapped[dict | None] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
