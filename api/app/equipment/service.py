"""Equipment control service — orchestrates validation, dispatch, and logging."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.equipment.interlocks import validate_interlocks
from app.equipment.models import ControllableEquipment, EquipmentStateLog
from app.equipment.protocols.dispatch import DispatchResult, dispatch_command, test_connection

logger = logging.getLogger(__name__)


async def execute_equipment_command(
    session: AsyncSession,
    equipment: ControllableEquipment,
    action: str,
    value: int | None = None,
    source: str = "user",
) -> tuple[bool, str, dict | None]:
    """Execute an equipment command with full interlock validation and state logging.

    Returns:
        (success, message, interlock_details) tuple.
        If interlock blocks, success=False with violation details.
    """
    # 1. Validate interlocks
    interlock_result = await validate_interlocks(session, equipment, action)
    if not interlock_result.allowed:
        # Log the interlock violation
        await _log_state_change(
            session=session,
            equipment=equipment,
            action=f"blocked_{action}",
            source="interlock",
            state_before=equipment.requested_state,
            state_after=equipment.requested_state,
            metadata={"violation": interlock_result.violation, **(interlock_result.details or {})},
        )
        return False, f"Interlock violation: {interlock_result.violation}", interlock_result.details

    # 2. Capture state before
    state_before = dict(equipment.requested_state)

    # 3. Dispatch command via protocol
    dispatch_result = await dispatch_command(equipment, action, value)

    if not dispatch_result.success:
        return False, dispatch_result.message, None

    # 4. Update requested state (optimistic)
    new_state = _compute_new_state(equipment.requested_state, action, value)
    equipment.requested_state = new_state
    equipment.updated_at = datetime.now(UTC)

    # 5. Log state change
    log_action = _normalize_action(action, value)
    await _log_state_change(
        session=session,
        equipment=equipment,
        action=log_action,
        source=source,
        state_before=state_before,
        state_after=new_state,
        metadata={"dispatch_message": dispatch_result.message},
    )

    await session.flush()
    return True, dispatch_result.message, None


async def confirm_equipment_state(
    session: AsyncSession,
    equipment: ControllableEquipment,
    confirmed_state: dict,
    source: str = "device_report",
) -> None:
    """Update equipment with confirmed state from device feedback."""
    state_before = dict(equipment.confirmed_state)
    equipment.confirmed_state = confirmed_state
    equipment.last_confirmed_at = datetime.now(UTC)
    equipment.updated_at = datetime.now(UTC)

    # Determine action from state change
    was_on = state_before.get("is_on", False)
    is_on = confirmed_state.get("is_on", False)
    if is_on and not was_on:
        action = "on"
    elif not is_on and was_on:
        action = "off"
    elif "power_w" in confirmed_state:
        action = "power_reading"
    else:
        action = "state_update"

    await _log_state_change(
        session=session,
        equipment=equipment,
        action=action,
        source=source,
        state_before=state_before,
        state_after=confirmed_state,
        metadata=None,
    )
    await session.flush()


async def force_off_equipment(
    session: AsyncSession,
    equipment: ControllableEquipment,
    source: str = "interlock",
    reason: str = "max_on_minutes exceeded",
) -> DispatchResult:
    """Force equipment OFF (used by watchdog and interlocks)."""
    state_before = dict(equipment.requested_state)

    result = await dispatch_command(equipment, "off")

    new_state = {"is_on": False}
    equipment.requested_state = new_state
    equipment.updated_at = datetime.now(UTC)

    await _log_state_change(
        session=session,
        equipment=equipment,
        action="interlock_off",
        source=source,
        state_before=state_before,
        state_after=new_state,
        metadata={"reason": reason, "dispatch_success": result.success},
    )
    await session.flush()
    return result


async def test_equipment_connection(
    equipment: ControllableEquipment,
) -> DispatchResult:
    """Test connectivity to equipment."""
    return await test_connection(equipment)


def _compute_new_state(current_state: dict, action: str, value: int | None) -> dict:
    """Compute the new requested state after a command."""
    new_state = dict(current_state)

    if action == "on":
        new_state["is_on"] = True
    elif action == "off":
        new_state["is_on"] = False
    elif action == "toggle":
        new_state["is_on"] = not new_state.get("is_on", False)
    elif action == "set_brightness":
        new_state["is_on"] = (value or 0) > 0
        new_state["brightness"] = value

    return new_state


def _normalize_action(action: str, value: int | None) -> str:
    """Normalize action for state log."""
    if action == "toggle":
        return "toggle"
    if action == "set_brightness":
        return "set_brightness"
    return action


async def _log_state_change(
    session: AsyncSession,
    equipment: ControllableEquipment,
    action: str,
    source: str,
    state_before: dict | None,
    state_after: dict | None,
    metadata: dict | None,
) -> EquipmentStateLog:
    """Write an entry to the equipment state log."""
    log = EquipmentStateLog(
        tenant_id=equipment.tenant_id,
        equipment_id=equipment.id,
        action=action,
        source=source,
        state_before=state_before,
        state_after=state_after,
        metadata_=metadata,
    )
    session.add(log)
    return log
