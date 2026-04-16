"""Automation API routes — rules CRUD, alert history, environment schedules."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.automation.models import AutomationRule, AlertHistory, EnvironmentSchedule

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


@router.post("/rules", response_model=RuleResponse, status_code=201)
async def create_rule(
    body: RuleCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    rule = AutomationRule(
        tenant_id=user.tenant_id,
        grow_cycle_id=UUID(body.grow_cycle_id) if body.grow_cycle_id else None,
        **body.model_dump(exclude={"grow_cycle_id"}),
    )
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


@router.get("/rules", response_model=list[RuleResponse])
async def list_rules(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_cycle_id: str | None = None,
):
    q = select(AutomationRule)
    if grow_cycle_id:
        q = q.where(AutomationRule.grow_cycle_id == UUID(grow_cycle_id))
    result = await session.execute(q)
    return result.scalars().all()


@router.patch("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: UUID,
    body: RuleUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
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


@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    limit: int = Query(default=50, le=200),
    acknowledged: bool | None = None,
):
    q = select(AlertHistory).order_by(desc(AlertHistory.created_at)).limit(limit)
    if acknowledged is not None:
        q = q.where(AlertHistory.acknowledged == acknowledged)
    result = await session.execute(q)
    return result.scalars().all()


@router.patch("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
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
    schedule = EnvironmentSchedule(
        tenant_id=user.tenant_id,
        tent_id=UUID(body.tent_id),
        **body.model_dump(exclude={"tent_id"}),
    )
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule


@router.get("/schedules", response_model=list[ScheduleResponse])
async def list_schedules(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    tent_id: str | None = None,
):
    q = select(EnvironmentSchedule)
    if tent_id:
        q = q.where(EnvironmentSchedule.tent_id == UUID(tent_id))
    result = await session.execute(q)
    return result.scalars().all()


@router.patch("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    body: ScheduleUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
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
    schedule = await session.get(EnvironmentSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await session.delete(schedule)
    await session.commit()
