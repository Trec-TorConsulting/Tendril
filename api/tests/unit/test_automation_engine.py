"""Tests for ``app.automation.engine.evaluate_rules`` \u2014 correctness +
query-count regression guard for the N+1 fix in PR #199.

These tests use the real Postgres test DB because the rewritten query
relies on Postgres' ``DISTINCT ON`` semantics.
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from app.automation import suppression
from app.automation.engine import evaluate_rules
from app.automation.models import AutomationRule
from app.grows.models import Bucket, BucketSensorReading, GrowCycle, Tent

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(autouse=True)
def _clear_suppression():
    suppression._reset_memory_for_tests()
    yield
    suppression._reset_memory_for_tests()


# Force suppression to use the in-memory fallback so the test isn't
# coupled to whatever Redis state the dev box has lying around.
@pytest.fixture(autouse=True)
def _disable_redis(monkeypatch):
    async def _no_redis():
        return None

    monkeypatch.setattr(suppression, "get_redis", _no_redis)


@pytest_asyncio.fixture
async def grow_with_buckets(tenant_factory):
    """Create a tenant with a grow cycle and 4 buckets, each with one reading.

    Returns ``(tenant_dict, grow, [bucket_1, ..., bucket_4])``.
    """
    tenant = await tenant_factory.create()
    session = tenant_factory.session

    tent = Tent(tenant_id=tenant["tenant"].id, name="test-tent")
    session.add(tent)
    await session.flush()

    grow = GrowCycle(
        tenant_id=tenant["tenant"].id,
        tent_id=tent.id,
        name="test-grow",
        grow_type="dwc",
        stage="late_veg",
        status="active",
    )
    session.add(grow)
    await session.flush()

    buckets: list[Bucket] = []
    # bucket 0: ph 5.5 (normal), bucket 1: ph 8.0 (alarm), bucket 2: ph 6.0 (normal),
    # bucket 3: no readings (should be skipped, not crash).
    for i, ph in enumerate([5.5, 8.0, 6.0, None]):
        bucket = Bucket(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            position=i + 1,
            growth_stage="late_veg",
        )
        session.add(bucket)
        await session.flush()
        buckets.append(bucket)
        if ph is not None:
            reading = BucketSensorReading(
                tenant_id=tenant["tenant"].id,
                bucket_id=bucket.id,
                ph=ph,
            )
            session.add(reading)

    # bucket 1 also gets an older, *normal* reading to verify DISTINCT ON
    # picks the latest, not an arbitrary row.
    from datetime import UTC, datetime, timedelta

    older = BucketSensorReading(
        tenant_id=tenant["tenant"].id,
        bucket_id=buckets[1].id,
        ph=6.0,
        recorded_at=datetime.now(UTC) - timedelta(hours=2),
    )
    session.add(older)

    await session.commit()
    return tenant, grow, buckets


class TestEvaluateRules:
    async def test_fires_alert_only_on_violating_bucket(self, grow_with_buckets, tenant_factory):
        tenant, grow, _buckets = grow_with_buckets
        session = tenant_factory.session

        rule = AutomationRule(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            name="pH high",
            sensor="ph",
            condition="gt",
            threshold=7.5,
            action="alert",
            severity="critical",
        )
        session.add(rule)
        await session.commit()

        alerts = await evaluate_rules(session)

        # Only bucket 1 (ph 8.0) should trip the rule. The older normal
        # reading on bucket 1 must be ignored because DISTINCT ON picks
        # the latest. bucket 3 has no readings and must not crash or fire.
        assert len(alerts) == 1
        assert alerts[0].sensor_value == 8.0

    async def test_no_alert_when_within_cooldown(self, grow_with_buckets, tenant_factory):
        tenant, grow, _buckets = grow_with_buckets
        session = tenant_factory.session

        from datetime import UTC, datetime

        rule = AutomationRule(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            name="pH high",
            sensor="ph",
            condition="gt",
            threshold=7.5,
            action="alert",
            severity="critical",
            cooldown_minutes=60,
            last_triggered=datetime.now(UTC),
        )
        session.add(rule)
        await session.commit()

        alerts = await evaluate_rules(session)
        assert alerts == []

    async def test_tenant_scoped_rule_with_no_grow_cycle_id(self, grow_with_buckets, tenant_factory):
        """Rule with grow_cycle_id=NULL should evaluate ALL tenant buckets."""
        tenant, _grow, _buckets = grow_with_buckets
        session = tenant_factory.session

        rule = AutomationRule(
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=None,
            name="pH high tenant-wide",
            sensor="ph",
            condition="gt",
            threshold=7.5,
            action="alert",
            severity="critical",
        )
        session.add(rule)
        await session.commit()

        alerts = await evaluate_rules(session)
        assert len(alerts) == 1
        assert alerts[0].sensor_value == 8.0


class TestQueryCount:
    async def test_evaluate_rules_query_count_is_bounded(self, grow_with_buckets, tenant_factory):
        """Regression guard: the rewrite in PR #199 brings query count from
        ``1 + R + R\u00d7B`` (\u2248 800 for a small tenant after PR #194 seeded
        47 defaults) down to a small constant tied to the number of
        distinct rule scopes \u2014 typically 2 to 4 for a real tenant.

        We use the SQLAlchemy ``after_cursor_execute`` event to count
        statements issued by the engine call.
        """
        tenant, grow, _buckets = grow_with_buckets
        session = tenant_factory.session

        # Add 10 rules, all scoped to the same grow_cycle, so the old
        # implementation would have issued 1 + 10 + 10\u00d74 = 51 queries.
        # The new implementation issues exactly 2: one for rules, one for
        # the latest-reading-per-bucket DISTINCT ON.
        for i in range(10):
            session.add(
                AutomationRule(
                    tenant_id=tenant["tenant"].id,
                    grow_cycle_id=grow.id,
                    name=f"ph rule {i}",
                    sensor="ph",
                    condition="gt",
                    threshold=10.0 + i,  # all non-firing
                    action="alert",
                    severity="info",
                )
            )
        await session.commit()

        # Wire up a SQLAlchemy event listener to count statements issued
        # by the engine call. The bound engine here is the sync engine
        # already (conftest mounts the test session via ``create_engine``
        # under ``run_sync``); falling back via ``getattr`` keeps this
        # robust if the conftest ever switches to ``create_async_engine``.
        from sqlalchemy import event

        bound = session.get_bind()
        sync_engine = getattr(bound, "sync_engine", bound)
        statements: list[str] = []

        def _record(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        event.listen(sync_engine, "after_cursor_execute", _record)
        try:
            await evaluate_rules(session)
        finally:
            event.remove(sync_engine, "after_cursor_execute", _record)

        # Expected: 1 rules query + 1 latest-readings DISTINCT ON.
        # Allow a tiny bit of slack for SQLAlchemy savepoint plumbing,
        # but the old code would emit ~51 here so anything <= 5 catches
        # the regression we care about.
        assert len(statements) <= 5, (
            f"evaluate_rules issued {len(statements)} statements (expected \u2264 5):\n" + "\n".join(statements)
        )
