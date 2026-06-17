"""Safety interlock validation for equipment control.

Enforces:
1. Cooldown periods between on-cycles
2. Max-on duration limits
3. Conflict detection (mutually exclusive equipment)
4. Rapid cycling prevention
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.equipment.models import ControllableEquipment, EquipmentStateLog

logger = logging.getLogger(__name__)

# Maximum toggles allowed in the rapid-cycling window
RAPID_CYCLE_MAX = 10
RAPID_CYCLE_WINDOW_MINUTES = 5


@dataclass
class InterlockResult:
    """Result of interlock validation."""

    allowed: bool
    violation: str | None = None
    details: dict | None = None


async def validate_interlocks(
    session: AsyncSession,
    equipment: ControllableEquipment,
    action: str,
) -> InterlockResult:
    """Validate all safety interlocks before allowing a command.

    Returns InterlockResult with allowed=True if command is safe to execute.
    """
    # Only enforce interlocks for "turn on" actions
    if action not in ("on", "toggle", "set_brightness"):
        return InterlockResult(allowed=True)

    # For toggle, check if it would result in ON
    if action == "toggle":
        current_on = equipment.requested_state.get("is_on", False)
        if current_on:
            # Toggle would turn OFF — always allowed
            return InterlockResult(allowed=True)

    # 1. Check cooldown period
    cooldown_result = await _check_cooldown(session, equipment)
    if not cooldown_result.allowed:
        return cooldown_result

    # 2. Check conflicts
    conflict_result = await _check_conflicts(session, equipment)
    if not conflict_result.allowed:
        return conflict_result

    # 3. Check rapid cycling
    rapid_result = await _check_rapid_cycling(session, equipment)
    if not rapid_result.allowed:
        return rapid_result

    return InterlockResult(allowed=True)


async def check_max_on_violations(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[ControllableEquipment]:
    """Find equipment that has exceeded its max_on_minutes.

    Called by the scheduler watchdog task.
    Returns list of equipment that needs to be force-turned-off.
    """
    now = datetime.now(UTC)

    # Find equipment that is ON and has a max_on_minutes limit
    stmt = select(ControllableEquipment).where(
        ControllableEquipment.tenant_id == tenant_id,
        ControllableEquipment.enabled.is_(True),
        ControllableEquipment.max_on_minutes.isnot(None),
    )
    equipment_list = (await session.execute(stmt)).scalars().all()

    violations: list[ControllableEquipment] = []
    for equip in equipment_list:
        is_on = equip.requested_state.get("is_on", False)
        if not is_on:
            continue

        # Find when it was last turned on
        last_on_log = (
            await session.execute(
                select(EquipmentStateLog)
                .where(
                    EquipmentStateLog.equipment_id == equip.id,
                    EquipmentStateLog.action == "on",
                )
                .order_by(EquipmentStateLog.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        if last_on_log is None:
            continue

        on_duration = now - last_on_log.created_at
        max_duration = timedelta(minutes=equip.max_on_minutes or 0)

        if on_duration > max_duration:
            violations.append(equip)

    return violations


async def _check_cooldown(
    session: AsyncSession,
    equipment: ControllableEquipment,
) -> InterlockResult:
    """Check if equipment is within its cooldown period."""
    if equipment.cooldown_minutes <= 0:
        return InterlockResult(allowed=True)

    now = datetime.now(UTC)
    cooldown_window = now - timedelta(minutes=equipment.cooldown_minutes)

    # Find the last OFF event
    last_off = (
        await session.execute(
            select(EquipmentStateLog)
            .where(
                EquipmentStateLog.equipment_id == equipment.id,
                EquipmentStateLog.action == "off",
                EquipmentStateLog.created_at >= cooldown_window,
            )
            .order_by(EquipmentStateLog.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if last_off is not None:
        remaining = equipment.cooldown_minutes - int((now - last_off.created_at).total_seconds() / 60)
        return InterlockResult(
            allowed=False,
            violation="cooldown",
            details={
                "equipment_id": str(equipment.id),
                "equipment_name": equipment.name,
                "cooldown_minutes": equipment.cooldown_minutes,
                "remaining_minutes": max(1, remaining),
            },
        )

    return InterlockResult(allowed=True)


async def _check_conflicts(
    session: AsyncSession,
    equipment: ControllableEquipment,
) -> InterlockResult:
    """Check if any conflicting equipment is currently active."""
    if not equipment.conflicts_with:
        return InterlockResult(allowed=True)

    # Load conflicting equipment
    stmt = select(ControllableEquipment).where(
        ControllableEquipment.id.in_(equipment.conflicts_with),
        ControllableEquipment.enabled.is_(True),
    )
    conflicts = (await session.execute(stmt)).scalars().all()

    active_conflicts = []
    for conflict in conflicts:
        if conflict.requested_state.get("is_on", False):
            active_conflicts.append({"id": str(conflict.id), "name": conflict.name})

    if active_conflicts:
        return InterlockResult(
            allowed=False,
            violation="conflict",
            details={
                "equipment_id": str(equipment.id),
                "equipment_name": equipment.name,
                "active_conflicts": active_conflicts,
            },
        )

    return InterlockResult(allowed=True)


async def _check_rapid_cycling(
    session: AsyncSession,
    equipment: ControllableEquipment,
) -> InterlockResult:
    """Check for rapid cycling (too many toggles in short window)."""
    now = datetime.now(UTC)
    window_start = now - timedelta(minutes=RAPID_CYCLE_WINDOW_MINUTES)

    toggle_count = (
        await session.execute(
            select(func.count(EquipmentStateLog.id)).where(
                EquipmentStateLog.equipment_id == equipment.id,
                EquipmentStateLog.action.in_(["on", "off", "toggle"]),
                EquipmentStateLog.created_at >= window_start,
            )
        )
    ).scalar_one()

    if toggle_count >= RAPID_CYCLE_MAX:
        return InterlockResult(
            allowed=False,
            violation="rapid_cycling",
            details={
                "equipment_id": str(equipment.id),
                "equipment_name": equipment.name,
                "toggles_in_window": toggle_count,
                "max_allowed": RAPID_CYCLE_MAX,
                "window_minutes": RAPID_CYCLE_WINDOW_MINUTES,
            },
        )

    return InterlockResult(allowed=True)
