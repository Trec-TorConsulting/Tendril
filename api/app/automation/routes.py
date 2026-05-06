"""Automation API routes — rules CRUD, alert history, environment schedules."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.automation.models import AlertHistory, AutomationRule, EnvironmentSchedule
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
    rule = AutomationRule(
        tenant_id=user.tenant_id,
        grow_cycle_id=UUID(body.grow_cycle_id) if body.grow_cycle_id else None,
        **body.model_dump(exclude={"grow_cycle_id"}),
    )
    session.add(rule)
    from app.billing.metering import record_usage

    await record_usage(session, user.tenant_id, "automations")
    await session.commit()
    await session.refresh(rule)
    return rule


@router.get("/rules", response_model=PaginatedResponse[RuleResponse])
async def list_rules(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: str | None = None,
):
    """List all automation rules for the current tenant."""
    q = select(AutomationRule).where(AutomationRule.tenant_id == user.tenant_id)
    if grow_cycle_id:
        q = q.where(AutomationRule.grow_cycle_id == UUID(grow_cycle_id))
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single automation rule by ID."""
    rule = await session.get(AutomationRule, rule_id)
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
    rule = await session.get(AutomationRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await session.commit()
    await session.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete an automation rule by ID."""
    rule = await session.get(AutomationRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await session.delete(rule)
    await session.commit()


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
    q = select(AlertHistory).order_by(desc(AlertHistory.created_at))
    if acknowledged is not None:
        q = q.where(AlertHistory.acknowledged == acknowledged)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single alert by ID."""
    alert = await session.get(AlertHistory, alert_id)
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
    alert = await session.get(AlertHistory, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    await session.commit()
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
    schedule = EnvironmentSchedule(
        tenant_id=user.tenant_id,
        tent_id=UUID(body.tent_id),
        **body.model_dump(exclude={"tent_id"}),
    )
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule


@router.get("/schedules", response_model=PaginatedResponse[ScheduleResponse])
async def list_schedules(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    tent_id: str | None = None,
):
    """List all automation schedules for the current tenant."""
    q = select(EnvironmentSchedule)
    if tent_id:
        q = q.where(EnvironmentSchedule.tent_id == UUID(tent_id))
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single environment schedule by ID."""
    schedule = await session.get(EnvironmentSchedule, schedule_id)
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
    schedule = await session.get(EnvironmentSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    await session.commit()
    await session.refresh(schedule)
    return schedule


@router.delete("/schedules/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete an automation schedule by ID."""
    schedule = await session.get(EnvironmentSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await session.delete(schedule)
    await session.commit()
