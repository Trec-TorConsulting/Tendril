"""Automation domain service.

Holds the business operations for automation rules, alert history, and
environment schedules. Route handlers in ``app.automation.routes`` are
HTTP-only — request parsing, response shaping, and ``HTTPException``
raising — and delegate all DB interaction to this module.

Conventions:
    * First positional argument is always ``session: AsyncSession``.
    * Functions return ORM model instances (or ``None`` for lookup misses);
      they never raise ``HTTPException``.
    * Query-builder helpers (``*_query``) return SQLAlchemy ``Select``
      objects so the route layer can hand them to ``app.pagination.paginate``.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.models import AlertHistory, AutomationRule, EnvironmentSchedule

# ─────────────────────────────────────────────────────────────────────────────
# Automation rules
# ─────────────────────────────────────────────────────────────────────────────


async def create_rule(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    grow_cycle_id: UUID | None,
    data: dict,
) -> AutomationRule:
    """Persist a new automation rule and record metered usage."""
    # Local import keeps the billing module out of automation's import cycle.
    from app.billing.metering import record_usage

    rule = AutomationRule(
        tenant_id=tenant_id,
        grow_cycle_id=grow_cycle_id,
        **data,
    )
    session.add(rule)
    await record_usage(session, tenant_id, "automations")
    await session.commit()
    await session.refresh(rule)
    return rule


def list_rules_query(
    *,
    tenant_id: UUID,
    grow_cycle_id: UUID | None = None,
) -> Select:
    """Build the query for listing rules; route layer paginates it."""
    q = select(AutomationRule).where(AutomationRule.tenant_id == tenant_id)
    if grow_cycle_id is not None:
        q = q.where(AutomationRule.grow_cycle_id == grow_cycle_id)
    return q


async def get_rule(session: AsyncSession, rule_id: UUID) -> AutomationRule | None:
    return await session.get(AutomationRule, rule_id)


async def update_rule(
    session: AsyncSession,
    rule: AutomationRule,
    updates: dict,
) -> AutomationRule:
    """Apply partial updates to a rule and commit."""
    for field, value in updates.items():
        setattr(rule, field, value)
    await session.commit()
    await session.refresh(rule)
    return rule


async def delete_rule(session: AsyncSession, rule: AutomationRule) -> None:
    await session.delete(rule)
    await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Alert history
# ─────────────────────────────────────────────────────────────────────────────


def list_alerts_query(*, acknowledged: bool | None = None) -> Select:
    """Build the alerts query ordered newest-first; route layer paginates."""
    q = select(AlertHistory).order_by(desc(AlertHistory.created_at))
    if acknowledged is not None:
        q = q.where(AlertHistory.acknowledged == acknowledged)
    return q


async def get_alert(session: AsyncSession, alert_id: UUID) -> AlertHistory | None:
    return await session.get(AlertHistory, alert_id)


async def acknowledge_alert(session: AsyncSession, alert: AlertHistory) -> None:
    """Mark an alert as acknowledged and commit."""
    alert.acknowledged = True
    await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Environment schedules
# ─────────────────────────────────────────────────────────────────────────────


async def create_schedule(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    tent_id: UUID,
    data: dict,
) -> EnvironmentSchedule:
    schedule = EnvironmentSchedule(
        tenant_id=tenant_id,
        tent_id=tent_id,
        **data,
    )
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule


def list_schedules_query(*, tent_id: UUID | None = None) -> Select:
    q = select(EnvironmentSchedule)
    if tent_id is not None:
        q = q.where(EnvironmentSchedule.tent_id == tent_id)
    return q


async def get_schedule(session: AsyncSession, schedule_id: UUID) -> EnvironmentSchedule | None:
    return await session.get(EnvironmentSchedule, schedule_id)


async def update_schedule(
    session: AsyncSession,
    schedule: EnvironmentSchedule,
    updates: dict,
) -> EnvironmentSchedule:
    for field, value in updates.items():
        setattr(schedule, field, value)
    await session.commit()
    await session.refresh(schedule)
    return schedule


async def delete_schedule(session: AsyncSession, schedule: EnvironmentSchedule) -> None:
    await session.delete(schedule)
    await session.commit()
