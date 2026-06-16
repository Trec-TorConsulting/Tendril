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

from app.automation.critical_alerts_defaults import CRITICAL_ALERTS, DEFAULTS_VERSION
from app.automation.models import AlertHistory, AutomationRule, EnvironmentSchedule
from app.tenants.models import Tenant

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
# System-default alert rules (seeding)
# ─────────────────────────────────────────────────────────────────────────────


def list_critical_rules_query(*, tenant_id: UUID, grow_type: str) -> Select:
    """Query for active critical rules a tenant has for a given grow type.

    Returns enabled rules where:
      * ``tenant_id`` matches,
      * ``grow_type`` matches (system defaults are always grow-type-keyed),
      * ``enabled`` is True.

    Used by the engine's ``evaluate_critical_alerts`` in place of the
    previously-hardcoded ``CRITICAL_ALERTS`` dict, so tenants can disable
    or override safety thresholds without code changes.
    """
    return select(AutomationRule).where(
        AutomationRule.tenant_id == tenant_id,
        AutomationRule.grow_type == grow_type,
        AutomationRule.enabled.is_(True),
    )


async def seed_system_alert_rules(
    session: AsyncSession,
    tenant_id: UUID,
    *,
    commit: bool = True,
) -> int:
    """Seed (or top-up) ``CRITICAL_ALERTS`` defaults into a tenant.

    Strategy:
      * Reads existing system-default rules for this tenant once.
      * Skips any default whose ``(grow_type, sensor, condition, threshold)``
        tuple already exists (matches both system rows and tenant-edited
        copies — we never overwrite or duplicate).
      * Stamps ``Tenant.system_alert_rules_seeded_version`` to the current
        ``DEFAULTS_VERSION`` so subsequent calls become no-ops until the
        version bumps.

    Returns the number of new rules inserted. Idempotent and safe to call
    repeatedly. The Alembic ``0047`` migration runs this for every existing
    tenant; ``app.auth.routes`` calls it for newly registered tenants.

    Caller controls the commit boundary via ``commit``. The migration
    runs inside its own transaction and passes ``commit=False``; the
    runtime hook in the registration flow commits the wider transaction
    itself.
    """
    tenant = await session.get(Tenant, tenant_id)
    if tenant is None:
        return 0

    # Pull existing rules once so the per-default check is in-memory.
    # The natural key of a system default is (grow_type, sensor, condition,
    # severity) — NOT threshold, because tenants edit threshold. Tiered
    # alerts (e.g. DWC water_temp_f gt 72 warning + gt 78 critical) are
    # disambiguated by severity. Verified unique across all 47 defaults.
    existing_rules = (
        await session.execute(
            select(
                AutomationRule.grow_type,
                AutomationRule.sensor,
                AutomationRule.condition,
                AutomationRule.severity,
            ).where(AutomationRule.tenant_id == tenant_id)
        )
    ).all()
    existing_signatures = {(gt, sensor, condition, severity) for gt, sensor, condition, severity in existing_rules}

    inserted = 0
    for grow_type, defaults in CRITICAL_ALERTS.items():
        for default in defaults:
            signature = (grow_type, default["sensor"], default["condition"], default["severity"])
            if signature in existing_signatures:
                continue
            session.add(
                AutomationRule(
                    tenant_id=tenant_id,
                    name=default["message"],
                    sensor=default["sensor"],
                    condition=default["condition"],
                    threshold=default["threshold"],
                    action="alert",
                    severity=default["severity"],
                    grow_type=grow_type,
                    is_system_default=True,
                    # Per-(rule, device) suppression is handled by
                    # ``app.automation.suppression``; rule cooldown is
                    # the legacy back-compat field. 0 here avoids any
                    # double-suppression for system defaults.
                    cooldown_minutes=0,
                )
            )
            inserted += 1

    if inserted and tenant.system_alert_rules_seeded_version < DEFAULTS_VERSION:
        tenant.system_alert_rules_seeded_version = DEFAULTS_VERSION
    elif not inserted and tenant.system_alert_rules_seeded_version < DEFAULTS_VERSION:
        # All defaults already exist (e.g. backfilled in migration), just
        # mark the version so the no-op detection works next time.
        tenant.system_alert_rules_seeded_version = DEFAULTS_VERSION

    if commit:
        await session.commit()
    else:
        await session.flush()
    return inserted


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
