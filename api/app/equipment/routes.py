"""Equipment control API routes."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.equipment.models import ControllableEquipment, EquipmentStateLog
from app.equipment.schemas import (
    EquipmentCommand,
    EquipmentCommandResponse,
    EquipmentCreate,
    EquipmentResponse,
    EquipmentUpdate,
    StateLogResponse,
    TestConnectionResponse,
)
from app.equipment.service import (
    execute_equipment_command,
    test_equipment_connection,
)
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


# ── CRUD ───────────────────────────────────────────────────────────────────────


@router.get("/", response_model=PaginatedResponse[EquipmentResponse])
async def list_equipment(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    tent_id: str | None = None,
    enabled: bool | None = None,
):
    """List controllable equipment for the tenant."""
    stmt = select(ControllableEquipment).where(ControllableEquipment.tenant_id == user.tenant_id)
    if tent_id:
        stmt = stmt.where(ControllableEquipment.tent_id == uuid.UUID(tent_id))
    if enabled is not None:
        stmt = stmt.where(ControllableEquipment.enabled == enabled)
    stmt = stmt.order_by(ControllableEquipment.name)

    page = await paginate(session, stmt, pagination)
    return PaginatedResponse(
        items=[_to_response(e) for e in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
    )


@router.post("/", response_model=EquipmentResponse, status_code=201)
async def create_equipment(
    body: EquipmentCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Register new controllable equipment."""
    equipment = ControllableEquipment(
        tenant_id=user.tenant_id,
        tent_id=uuid.UUID(body.tent_id) if body.tent_id else None,
        name=body.name,
        equipment_type=body.equipment_type,
        protocol=body.protocol,
        protocol_config=body.protocol_config,
        capabilities=body.capabilities,
        requested_state={"is_on": False},
        confirmed_state={},
        max_on_minutes=body.max_on_minutes,
        cooldown_minutes=body.cooldown_minutes,
        conflicts_with=[uuid.UUID(c) for c in body.conflicts_with],
    )
    session.add(equipment)
    await session.commit()
    await session.refresh(equipment)
    return _to_response(equipment)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single equipment record."""
    equipment = await _get_equipment_or_404(session, equipment_id, user.tenant_id)
    return _to_response(equipment)


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: str,
    body: EquipmentUpdate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update equipment configuration."""
    equipment = await _get_equipment_or_404(session, equipment_id, user.tenant_id)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tent_id":
            setattr(equipment, field, uuid.UUID(value) if value else None)
        elif field == "conflicts_with":
            setattr(equipment, field, [uuid.UUID(c) for c in value] if value else [])
        else:
            setattr(equipment, field, value)

    equipment.updated_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(equipment)
    return _to_response(equipment)


@router.delete("/{equipment_id}", status_code=204)
async def delete_equipment(
    equipment_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete equipment. Sends OFF command if currently on."""
    equipment = await _get_equipment_or_404(session, equipment_id, user.tenant_id)

    # Safety: turn off before deletion if currently on
    if equipment.requested_state.get("is_on", False):
        from app.equipment.protocols.dispatch import dispatch_command

        await dispatch_command(equipment, "off")

    await session.delete(equipment)
    await session.commit()


# ── Commands ───────────────────────────────────────────────────────────────────


@router.post("/{equipment_id}/command", response_model=EquipmentCommandResponse)
async def send_command(
    equipment_id: str,
    body: EquipmentCommand,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Send a control command to equipment."""
    equipment = await _get_equipment_or_404(session, equipment_id, user.tenant_id)

    if not equipment.enabled:
        raise HTTPException(status_code=400, detail="Equipment is disabled")

    success, message, interlock_details = await execute_equipment_command(
        session=session,
        equipment=equipment,
        action=body.action,
        value=body.value,
        source="user",
    )

    if not success and interlock_details:
        raise HTTPException(status_code=409, detail={"violation": message, **interlock_details})

    if not success:
        raise HTTPException(status_code=502, detail=message)

    await session.commit()
    await session.refresh(equipment)

    return EquipmentCommandResponse(
        equipment_id=str(equipment.id),
        action=body.action,
        success=True,
        requested_state=equipment.requested_state,
        message=message,
    )


# ── State History ──────────────────────────────────────────────────────────────


@router.get("/{equipment_id}/history", response_model=PaginatedResponse[StateLogResponse])
async def get_state_history(
    equipment_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    source: str | None = None,
):
    """Get equipment state change history."""
    # Verify equipment belongs to tenant
    await _get_equipment_or_404(session, equipment_id, user.tenant_id)

    stmt = select(EquipmentStateLog).where(
        EquipmentStateLog.equipment_id == uuid.UUID(equipment_id),
        EquipmentStateLog.tenant_id == user.tenant_id,
    )
    if source:
        stmt = stmt.where(EquipmentStateLog.source == source)
    stmt = stmt.order_by(EquipmentStateLog.created_at.desc())

    page = await paginate(session, stmt, pagination)
    return PaginatedResponse(
        items=[_to_log_response(log) for log in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
    )


# ── Test Connection ────────────────────────────────────────────────────────────


@router.post("/{equipment_id}/test", response_model=TestConnectionResponse)
async def test_connection_endpoint(
    equipment_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Test connectivity to equipment device."""
    equipment = await _get_equipment_or_404(session, equipment_id, user.tenant_id)

    result = await test_equipment_connection(equipment)
    return TestConnectionResponse(
        reachable=result.success,
        protocol=equipment.protocol,
        message=result.message,
        device_info=result.device_info,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────


async def _get_equipment_or_404(
    session: AsyncSession,
    equipment_id: str,
    tenant_id: uuid.UUID,
) -> ControllableEquipment:
    """Load equipment by ID, raise 404 if not found or wrong tenant."""
    try:
        uid = uuid.UUID(equipment_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid equipment_id format") from err

    equipment = await session.get(ControllableEquipment, uid)
    if equipment is None or equipment.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


def _to_response(equipment: ControllableEquipment) -> EquipmentResponse:
    """Convert model to response schema."""
    return EquipmentResponse(
        id=str(equipment.id),
        tenant_id=str(equipment.tenant_id),
        tent_id=str(equipment.tent_id) if equipment.tent_id else None,
        name=equipment.name,
        equipment_type=equipment.equipment_type,
        protocol=equipment.protocol,
        protocol_config=equipment.protocol_config,
        capabilities=equipment.capabilities,
        requested_state=equipment.requested_state,
        confirmed_state=equipment.confirmed_state,
        last_confirmed_at=equipment.last_confirmed_at,
        max_on_minutes=equipment.max_on_minutes,
        cooldown_minutes=equipment.cooldown_minutes,
        conflicts_with=[str(c) for c in (equipment.conflicts_with or [])],
        enabled=equipment.enabled,
        created_at=equipment.created_at,
        updated_at=equipment.updated_at,
    )


def _to_log_response(log: EquipmentStateLog) -> StateLogResponse:
    """Convert state log model to response schema."""
    return StateLogResponse(
        id=str(log.id),
        equipment_id=str(log.equipment_id),
        action=log.action,
        source=log.source,
        state_before=log.state_before,
        state_after=log.state_after,
        metadata_=log.metadata_,
        created_at=log.created_at,
    )
