"""Automation models — rules, schedules, alert history."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    grow_cycle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sensor: Mapped[str] = mapped_column(String(50), nullable=False)  # ph, ec, water_temp, etc.
    condition: Mapped[str] = mapped_column(String(10), nullable=False)  # gt, lt, gte, lte, eq
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # alert, dose_ph_up, dose_ph_down, notify, etc.
    action_params: Mapped[dict | None] = mapped_column(JSON)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=30)
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # info, warning, critical
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    # Grow-type-keyed system rules. Nullable for tenant-authored rules that
    # apply to all grow types (or that target a specific grow_cycle_id).
    grow_type: Mapped[str | None] = mapped_column(String(50), index=True)
    # True for safety-net defaults seeded from
    # ``app.automation.critical_alerts_defaults.CRITICAL_ALERTS``. UI may
    # surface these differently (e.g. "system default — reset to default"
    # control) but the engine treats them identically.
    is_system_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_triggered: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("automation_rules.id"))
    grow_cycle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="SET NULL")
    )
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sensor_value: Mapped[float | None] = mapped_column(Float)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class EnvironmentSchedule(Base):
    __tablename__ = "environment_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    tent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tents.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # light, fan, hvac, pump
    stage: Mapped[str | None] = mapped_column(String(50))  # vegetative, flowering, etc.
    on_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    off_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    settings: Mapped[dict | None] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
