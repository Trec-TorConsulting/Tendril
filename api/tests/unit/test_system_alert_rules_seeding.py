"""Tests for ``app.automation.service.seed_system_alert_rules`` and the
DB-backed ``evaluate_critical_alerts`` path that depends on it.
"""

from __future__ import annotations

import uuid

import pytest

from app.automation.critical_alerts_defaults import CRITICAL_ALERTS, DEFAULTS_VERSION
from app.automation.engine import evaluate_critical_alerts
from app.automation.models import AutomationRule
from app.automation.service import seed_system_alert_rules
from app.grows.models import Bucket, BucketSensorReading, GrowCycle, Tent
from app.tenants.models import Tenant


@pytest.mark.asyncio
class TestSeedSystemAlertRules:
    async def test_seeds_all_defaults_for_fresh_tenant(self, tenant_factory):
        tenant = await tenant_factory.create()
        session = tenant_factory.session

        inserted = await seed_system_alert_rules(session, tenant["tenant"].id)

        # 47 system rules expected (17 grow types, varies per type).
        expected_total = sum(len(rules) for rules in CRITICAL_ALERTS.values())
        assert inserted == expected_total

        # Tenant version stamp should advance.
        await session.refresh(tenant["tenant"])
        assert tenant["tenant"].system_alert_rules_seeded_version == DEFAULTS_VERSION

    async def test_idempotent_second_call_is_noop(self, tenant_factory):
        tenant = await tenant_factory.create()
        session = tenant_factory.session

        first = await seed_system_alert_rules(session, tenant["tenant"].id)
        second = await seed_system_alert_rules(session, tenant["tenant"].id)

        assert first > 0
        assert second == 0

    async def test_seeded_rules_carry_grow_type_and_system_flag(self, tenant_factory):
        tenant = await tenant_factory.create()
        session = tenant_factory.session

        await seed_system_alert_rules(session, tenant["tenant"].id)

        from sqlalchemy import select

        rules = (
            (
                await session.execute(
                    select(AutomationRule).where(
                        AutomationRule.tenant_id == tenant["tenant"].id,
                        AutomationRule.is_system_default.is_(True),
                    )
                )
            )
            .scalars()
            .all()
        )

        assert len(rules) > 0
        for rule in rules:
            assert rule.is_system_default is True
            assert rule.grow_type is not None
            assert rule.grow_type in CRITICAL_ALERTS
            assert rule.action == "alert"
            assert rule.enabled is True

    async def test_does_not_overwrite_tenant_edits(self, tenant_factory):
        """If a tenant has edited a seeded rule, reseeding must not overwrite."""
        tenant = await tenant_factory.create()
        session = tenant_factory.session

        # Seed once.
        await seed_system_alert_rules(session, tenant["tenant"].id)

        # Tenant retunes the DWC dissolved-oxygen rule.
        from sqlalchemy import select

        dwc_do_rule = (
            (
                await session.execute(
                    select(AutomationRule).where(
                        AutomationRule.tenant_id == tenant["tenant"].id,
                        AutomationRule.grow_type == "dwc",
                        AutomationRule.sensor == "dissolved_oxygen",
                    )
                )
            )
            .scalars()
            .one()
        )
        dwc_do_rule.threshold = 3.0  # tenant lowered the alarm threshold
        await session.commit()

        # Reseed (e.g. a new deploy).
        inserted = await seed_system_alert_rules(session, tenant["tenant"].id)

        # No new rules inserted; tenant edit preserved.
        assert inserted == 0
        await session.refresh(dwc_do_rule)
        assert dwc_do_rule.threshold == 3.0

    async def test_two_tenants_get_independent_copies(self, tenant_factory):
        tenant_a = await tenant_factory.create()
        tenant_b = await tenant_factory.create()
        session = tenant_factory.session

        await seed_system_alert_rules(session, tenant_a["tenant"].id)
        await seed_system_alert_rules(session, tenant_b["tenant"].id)

        from sqlalchemy import func, select

        count_a = (
            await session.execute(
                select(func.count(AutomationRule.id)).where(AutomationRule.tenant_id == tenant_a["tenant"].id)
            )
        ).scalar_one()
        count_b = (
            await session.execute(
                select(func.count(AutomationRule.id)).where(AutomationRule.tenant_id == tenant_b["tenant"].id)
            )
        ).scalar_one()

        expected = sum(len(rules) for rules in CRITICAL_ALERTS.values())
        assert count_a == expected
        assert count_b == expected

    async def test_unknown_tenant_returns_zero(self, db_session):
        inserted = await seed_system_alert_rules(db_session, uuid.uuid4())
        assert inserted == 0

    async def test_version_stamp_advances_even_when_all_rules_pre_exist(self, tenant_factory):
        """If a previous (failed) seed inserted every rule but didn't stamp
        the version, a retry should still stamp it."""
        tenant_obj = (await tenant_factory.create())["tenant"]
        session = tenant_factory.session

        # First seed: rows go in, version stamps.
        await seed_system_alert_rules(session, tenant_obj.id)

        # Simulate the bad state: reset version manually.
        from sqlalchemy import select

        t = (await session.execute(select(Tenant).where(Tenant.id == tenant_obj.id))).scalar_one()
        t.system_alert_rules_seeded_version = 0
        await session.commit()

        # Retry: no rows to add, but version should advance again.
        inserted = await seed_system_alert_rules(session, tenant_obj.id)
        assert inserted == 0
        await session.refresh(t)
        assert t.system_alert_rules_seeded_version == DEFAULTS_VERSION


@pytest.mark.asyncio
class TestDeleteSystemRuleForbidden:
    async def test_cannot_delete_system_default_rule(self, tenant_factory, client):
        tenant = await tenant_factory.create()
        session = tenant_factory.session

        await seed_system_alert_rules(session, tenant["tenant"].id)

        from sqlalchemy import select

        system_rule = (
            (
                await session.execute(
                    select(AutomationRule).where(
                        AutomationRule.tenant_id == tenant["tenant"].id,
                        AutomationRule.is_system_default.is_(True),
                    )
                )
            )
            .scalars()
            .first()
        )

        resp = await client.delete(
            f"/v1/automation/rules/{system_rule.id}",
            headers=tenant["headers"],
        )
        assert resp.status_code == 409
        assert "system-default" in resp.json()["detail"].lower()

    # Note: PATCH-based disable is exercised by the generic
    # ``test_update_rule`` in ``tests/unit/test_automation.py`` — the
    # ``is_system_default`` flag has no special semantics for updates.


@pytest.mark.asyncio
class TestStageAwareCriticalAlertEvaluation:
    async def test_stage_defaults_can_trigger_below_persisted_threshold(self, tenant_factory):
        tenant = await tenant_factory.create()
        session = tenant_factory.session

        tent = Tent(tenant_id=tenant["tenant"].id, name="stage-aware-test")
        session.add(tent)
        await session.flush()

        grow = GrowCycle(
            tenant_id=tenant["tenant"].id,
            tent_id=tent.id,
            name="flower-grow",
            grow_type="dwc",
            stage="flowering",
            status="active",
        )
        session.add(grow)
        await session.flush()

        bucket = Bucket(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            position=1,
            growth_stage="flowering",
        )
        session.add(bucket)
        await session.flush()

        reading = BucketSensorReading(
            tenant_id=tenant["tenant"].id,
            bucket_id=bucket.id,
            ec=2.3,
        )
        session.add(reading)

        # Persisted threshold is 2.5, but stage-aware default for flowering EC
        # is lower (2.2), so this should still trigger.
        rule = AutomationRule(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            grow_type="dwc",
            is_system_default=True,
            name="DWC EC high",
            sensor="ec",
            condition="gt",
            threshold=2.5,
            action="alert",
            severity="warning",
        )
        session.add(rule)
        await session.commit()

        alerts = await evaluate_critical_alerts(
            session,
            grow.grow_type,
            tenant["tenant"].id,
            grow.id,
            reading,
        )

        assert len(alerts) == 1
        assert alerts[0].sensor_value == 2.3
        assert "stage 'flowering'" in alerts[0].message

    async def test_rule_stage_threshold_override_takes_precedence(self, tenant_factory):
        tenant = await tenant_factory.create()
        session = tenant_factory.session

        tent = Tent(tenant_id=tenant["tenant"].id, name="override-test")
        session.add(tent)
        await session.flush()

        grow = GrowCycle(
            tenant_id=tenant["tenant"].id,
            tent_id=tent.id,
            name="veg-grow",
            grow_type="dwc",
            stage="vegetative",
            status="active",
        )
        session.add(grow)
        await session.flush()

        bucket = Bucket(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            position=1,
            growth_stage="vegetative",
        )
        session.add(bucket)
        await session.flush()

        reading = BucketSensorReading(
            tenant_id=tenant["tenant"].id,
            bucket_id=bucket.id,
            ec=1.2,
        )
        session.add(reading)

        rule = AutomationRule(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            grow_type="dwc",
            is_system_default=True,
            name="DWC EC tuned",
            sensor="ec",
            condition="gt",
            threshold=2.5,
            action="alert",
            severity="warning",
            action_params={"stage_thresholds": {"vegetative": {"gt": 1.0}}},
        )
        session.add(rule)
        await session.commit()

        alerts = await evaluate_critical_alerts(
            session,
            grow.grow_type,
            tenant["tenant"].id,
            grow.id,
            reading,
        )

        assert len(alerts) == 1
        assert "gt 1.0" in alerts[0].message
