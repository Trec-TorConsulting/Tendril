"""Device command framework — queue and dispatch commands to ESP32/Tuya devices."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import DateTime, ForeignKey, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.database import Base
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.tenants.models import Device

logger = logging.getLogger("tendril.devices.commands")

router = APIRouter()


# ── Models ─────────────────────────────────────────────────────────────────────


class CommandStatus(StrEnum):
    pending = "pending"
    sent = "sent"
    acknowledged = "acknowledged"
    failed = "failed"
    expired = "expired"


class DeviceCommand(Base):
    __tablename__ = "device_commands"

    id: Mapped[uuid.UUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        SA_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    command_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(50), default="user")  # user, automation, schedule


# ── Supported command types ────────────────────────────────────────────────────

COMMAND_TYPES = {
    # Relay/actuator control
    "relay_on": "Turn a relay on (payload: {relay_id: int})",
    "relay_off": "Turn a relay off (payload: {relay_id: int})",
    "relay_pulse": "Pulse a relay for N seconds (payload: {relay_id: int, duration_s: float})",
    # Pump control
    "pump_start": "Start a pump (payload: {pump_id: int, duration_s?: float})",
    "pump_stop": "Stop a pump (payload: {pump_id: int})",
    # pH dosing
    "dose_ph_up": "Dispense pH up solution (payload: {ml: float})",
    "dose_ph_down": "Dispense pH down solution (payload: {ml: float})",
    # Nutrient dosing
    "dose_nutrient": "Dispense nutrient (payload: {channel: int, ml: float})",
    # Environment
    "set_light_schedule": "Set light on/off times (payload: {on_time: str, off_time: str})",
    "set_fan_speed": "Set fan speed percent (payload: {speed_pct: int})",
    # Irrigation
    "irrigate": "Run irrigation for duration (payload: {zone: int, duration_s: float})",
    # Device management
    "reboot": "Reboot device (payload: {})",
    "ota_update": "Trigger OTA firmware update (payload: {url: str})",
    "set_poll_interval": "Change sensor poll interval (payload: {interval_s: int})",
    # Tuya-specific
    "tuya_set_dp": "Set a Tuya data point (payload: {dp_id: int, value: any})",
}


# ── Schemas ────────────────────────────────────────────────────────────────────


class CommandCreate(BaseModel):
    device_id: str
    command_type: str
    payload: dict = {}
    expires_in_seconds: int | None = 300  # Default 5 min expiry


class CommandResponse(BaseModel):
    id: str
    device_id: str
    command_type: str
    payload: dict
    status: str
    source: str
    created_at: str
    sent_at: str | None
    acknowledged_at: str | None
    error_message: str | None

    class Config:
        from_attributes = True


class CommandAck(BaseModel):
    status: str = "acknowledged"
    error_message: str | None = None


# ── Routes ─────────────────────────────────────────────────────────────────────


@router.post("/commands", response_model=CommandResponse)
async def create_command(
    body: CommandCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Queue a command for a device. The command will be delivered on next device poll or via MQTT publish."""
    if body.command_type not in COMMAND_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown command_type '{body.command_type}'. Valid types: {list(COMMAND_TYPES.keys())}",
        )

    # Verify device belongs to tenant
    device = (
        await session.execute(
            select(Device).where(Device.device_id == body.device_id, Device.tenant_id == user.tenant_id)
        )
    ).scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status != "paired":
        raise HTTPException(status_code=400, detail="Device must be paired to receive commands")

    now = datetime.now(UTC)
    from datetime import timedelta

    cmd = DeviceCommand(
        tenant_id=user.tenant_id,
        device_id=body.device_id,
        command_type=body.command_type,
        payload=json.dumps(body.payload),
        status="pending",
        source="user",
        expires_at=now + timedelta(seconds=body.expires_in_seconds) if body.expires_in_seconds else None,
    )
    session.add(cmd)
    await session.commit()
    await session.refresh(cmd)

    # Attempt immediate MQTT delivery
    delivered = await _try_mqtt_deliver(cmd)
    if delivered:
        cmd.status = "sent"
        cmd.sent_at = datetime.now(UTC)
        await session.commit()

    return _to_response(cmd)


@router.get("/commands", response_model=PaginatedResponse[CommandResponse])
async def list_commands(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    device_id: str | None = None,
    status: str | None = None,
):
    """List queued/sent commands for tenant devices."""
    q = select(DeviceCommand).where(DeviceCommand.tenant_id == user.tenant_id)
    if device_id:
        q = q.where(DeviceCommand.device_id == device_id)
    if status:
        q = q.where(DeviceCommand.status == status)
    q = q.order_by(DeviceCommand.created_at.desc())
    page = await paginate(session, q, pagination)
    return PaginatedResponse(
        items=[_to_response(c) for c in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
    )


@router.get("/commands/{command_id}", response_model=CommandResponse)
async def get_command(
    command_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single command by ID."""
    cmd = await session.get(DeviceCommand, uuid.UUID(command_id))
    if not cmd or cmd.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Command not found")
    return _to_response(cmd)


@router.get("/commands/pending/{device_id}")
async def get_pending_commands(
    device_id: str,
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get pending commands for a device (called by device firmware on poll)."""
    now = datetime.now(UTC)
    cmds = (
        (
            await session.execute(
                select(DeviceCommand).where(
                    DeviceCommand.device_id == device_id,
                    DeviceCommand.tenant_id == user.tenant_id,
                    DeviceCommand.status == "pending",
                )
            )
        )
        .scalars()
        .all()
    )

    # Filter out expired commands
    result = []
    for cmd in cmds:
        if cmd.expires_at and cmd.expires_at < now:
            cmd.status = "expired"
        else:
            cmd.status = "sent"
            cmd.sent_at = now
            result.append(_to_response(cmd))

    await session.commit()
    return result


@router.post("/commands/{command_id}/ack")
async def acknowledge_command(
    command_id: str,
    body: CommandAck,
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Device acknowledges command execution (success or failure)."""
    cmd = await session.get(DeviceCommand, uuid.UUID(command_id))
    if not cmd or cmd.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Command not found")

    now = datetime.now(UTC)
    if body.status == "acknowledged":
        cmd.status = "acknowledged"
        cmd.acknowledged_at = now
    elif body.status == "failed":
        cmd.status = "failed"
        cmd.error_message = body.error_message
        cmd.acknowledged_at = now
    else:
        raise HTTPException(status_code=400, detail="status must be 'acknowledged' or 'failed'")

    await session.commit()
    return {"status": "ok"}


@router.get("/commands/types")
async def list_command_types(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List available command types and their descriptions."""
    return [{"type": k, "description": v} for k, v in COMMAND_TYPES.items()]


# ── Helpers ────────────────────────────────────────────────────────────────────


def _to_response(cmd: DeviceCommand) -> CommandResponse:
    return CommandResponse(
        id=str(cmd.id),
        device_id=cmd.device_id,
        command_type=cmd.command_type,
        payload=json.loads(cmd.payload) if isinstance(cmd.payload, str) else cmd.payload,
        status=cmd.status,
        source=cmd.source,
        created_at=cmd.created_at.isoformat() if cmd.created_at else "",
        sent_at=cmd.sent_at.isoformat() if cmd.sent_at else None,
        acknowledged_at=cmd.acknowledged_at.isoformat() if cmd.acknowledged_at else None,
        error_message=cmd.error_message,
    )


async def _try_mqtt_deliver(cmd: DeviceCommand) -> bool:
    """Attempt to publish command via MQTT. Returns True if published successfully."""
    try:
        from app.mqtt.publisher import publish_command

        topic = f"t/{cmd.tenant_id}/d/{cmd.device_id}/command/{cmd.command_type}"
        payload_str = cmd.payload if isinstance(cmd.payload, str) else json.dumps(cmd.payload)
        await publish_command(topic, payload_str)
        return True
    except ImportError:
        # MQTT publisher not yet available — command will be picked up on device poll
        logger.debug("MQTT publisher not available — command %s queued for poll", cmd.id)
        return False
    except Exception:
        logger.debug("MQTT publish failed for command %s — queued for poll", cmd.id, exc_info=True)
        return False


async def send_command_from_automation(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    device_id: str,
    command_type: str,
    payload: dict,
    source: str = "automation",
) -> DeviceCommand:
    """Create and attempt delivery of a command from an automation rule or schedule.

    This is the programmatic entry point used by the automation engine and scheduler.
    """
    from datetime import timedelta

    now = datetime.now(UTC)
    cmd = DeviceCommand(
        tenant_id=tenant_id,
        device_id=device_id,
        command_type=command_type,
        payload=json.dumps(payload),
        status="pending",
        source=source,
        expires_at=now + timedelta(seconds=300),
    )
    session.add(cmd)
    await session.flush()

    delivered = await _try_mqtt_deliver(cmd)
    if delivered:
        cmd.status = "sent"
        cmd.sent_at = datetime.now(UTC)

    return cmd
