"""SQLAlchemy models for controllable equipment and state logging."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy import UUID as SA_UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ControllableEquipment(Base):
    """A controllable relay, outlet, dimmer, or smart plug device."""

    __tablename__ = "controllable_equipment"

    id: Mapped[uuid.UUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tent_id: Mapped[uuid.UUID | None] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("tents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    protocol: Mapped[str] = mapped_column(String(30), nullable=False)
    protocol_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    capabilities: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    requested_state: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    confirmed_state: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    last_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    max_on_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conflicts_with: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(SA_UUID(as_uuid=True)), nullable=False, default=list)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    state_logs: Mapped[list[EquipmentStateLog]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan", lazy="dynamic"
    )


class EquipmentStateLog(Base):
    """Audit trail of equipment state changes."""

    __tablename__ = "equipment_state_log"

    id: Mapped[uuid.UUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        ForeignKey("controllable_equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    state_before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    state_after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata_", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

    # Relationships
    equipment: Mapped[ControllableEquipment] = relationship(back_populates="state_logs")


# Valid equipment types
EQUIPMENT_TYPES = {"relay", "dimmer", "smart_plug", "pump", "fan_controller"}

# Valid protocols
PROTOCOLS = {"tasmota_mqtt", "shelly_http", "tuya_cloud", "kasa_local", "generic_mqtt"}

# Valid capabilities
CAPABILITIES = {"on_off", "dimmer", "power_monitor", "energy_meter"}

# Valid actions for state log
STATE_LOG_ACTIONS = {
    "on",
    "off",
    "toggle",
    "set_brightness",
    "power_reading",
    "interlock_off",
}

# Valid sources for state log
STATE_LOG_SOURCES = {"user", "automation", "schedule", "interlock", "device_report"}
