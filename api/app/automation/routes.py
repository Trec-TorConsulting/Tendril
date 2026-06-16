"""Automation API routes — rules CRUD, alert history, environment schedules.

This module is HTTP-only. All persistence and domain logic lives in
``app.automation.service``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.automation import service
from app.billing.tier_gate import require_usage_limit
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


# ---------- Automation Rules ----------


class RuleCreate(BaseModel):
    grow_cycle_id: str | None = None
    name: str
    sensor: str
    condition: str
    threshold: float
    action: str
    action_params: dict | None = None
    cooldown_minutes: int = 30
    severity: str = "warning"


class RuleUpdate(BaseModel):
    name: str | None = None
    threshold: float | None = None
    action: str | None = None
    cooldown_minutes: int | None = None
    severity: str | None = None
    enabled: bool | None = None


class RuleResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID | None
    name: str
    sensor: str
    condition: str
    threshold: float
    action: str
    action_params: dict | None
    cooldown_minutes: int
    severity: str
    enabled: bool
    last_triggered: datetime | None
    model_config = {"from_attributes": True}


@router.post(
    "/rules",
    response_model=RuleResponse,
    status_code=201,
    dependencies=[Depends(require_usage_limit("automations"))],
)
async def create_rule(
    body: RuleCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new automation rule for threshold-based alerts."""
    return await service.create_rule(
        session,
        tenant_id=user.tenant_id,
        grow_cycle_id=UUID(body.grow_cycle_id) if body.grow_cycle_id else None,
        data=body.model_dump(exclude={"grow_cycle_id"}),
    )


@router.get("/rules", response_model=PaginatedResponse[RuleResponse])
async def list_rules(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: str | None = None,
):
    """List all automation rules for the current tenant."""
    q = service.list_rules_query(
        tenant_id=user.tenant_id,
        grow_cycle_id=UUID(grow_cycle_id) if grow_cycle_id else None,
    )
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single automation rule by ID."""
    rule = await service.get_rule(session, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.patch("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: UUID,
    body: RuleUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update an existing automation rule."""
    rule = await service.get_rule(session, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return await service.update_rule(session, rule, body.model_dump(exclude_unset=True))


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete an automation rule by ID."""
    rule = await service.get_rule(session, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await service.delete_rule(session, rule)


# ---------- Alert History ----------


class AlertResponse(BaseModel):
    id: UUID
    rule_id: UUID | None
    grow_cycle_id: UUID | None
    alert_type: str
    severity: str
    message: str
    sensor_value: float | None
    acknowledged: bool
    created_at: datetime
    model_config = {"from_attributes": True}


@router.get("/alerts", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    acknowledged: bool | None = None,
):
    """List triggered alerts with optional status filtering."""
    q = service.list_alerts_query(acknowledged=acknowledged)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single alert by ID."""
    alert = await service.get_alert(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/alerts/{alert_id}/acknowledge", response_model=dict)
async def acknowledge_alert(
    alert_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Acknowledge a triggered alert."""
    alert = await service.get_alert(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await service.acknowledge_alert(session, alert)
    return {"status": "acknowledged"}


# ---------- Environment Schedules ----------


class ScheduleCreate(BaseModel):
    tent_id: str
    name: str
    schedule_type: str
    stage: str | None = None
    on_time: str
    off_time: str
    settings: dict | None = None


class ScheduleUpdate(BaseModel):
    name: str | None = None
    stage: str | None = None
    on_time: str | None = None
    off_time: str | None = None
    settings: dict | None = None
    enabled: bool | None = None


class ScheduleResponse(BaseModel):
    id: UUID
    tent_id: UUID
    name: str
    schedule_type: str
    stage: str | None
    on_time: str
    off_time: str
    settings: dict | None
    enabled: bool
    model_config = {"from_attributes": True}


@router.post("/schedules", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    body: ScheduleCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a scheduled automation action."""
    return await service.create_schedule(
        session,
        tenant_id=user.tenant_id,
        tent_id=UUID(body.tent_id),
        data=body.model_dump(exclude={"tent_id"}),
    )


@router.get("/schedules", response_model=PaginatedResponse[ScheduleResponse])
async def list_schedules(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    tent_id: str | None = None,
):
    """List all automation schedules for the current tenant."""
    q = service.list_schedules_query(tent_id=UUID(tent_id) if tent_id else None)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single environment schedule by ID."""
    schedule = await service.get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.patch("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    body: ScheduleUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update an existing automation schedule."""
    schedule = await service.get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return await service.update_schedule(session, schedule, body.model_dump(exclude_unset=True))


@router.delete("/schedules/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete an automation schedule by ID."""
    schedule = await service.get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await service.delete_schedule(session, schedule)
