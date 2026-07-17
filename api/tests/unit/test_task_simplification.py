"""Tests for the simplified recurring-seed task generation model.

Covers:
- Generator emits at most one open seed per template/grow
- Generator is idempotent (re-run produces no duplicates)
- complete_task rolls forward overdue occurrence
- every_2_days / every_3_days recurrence works end-to-end
- skip advances without completing
- routine-grouped endpoint returns grouped results
- _next_due_delta covers all label patterns
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def commercial_tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(plan="commercial")


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests for _next_due_delta (no DB required)
# ─────────────────────────────────────────────────────────────────────────────


class TestNextDueDelta:
    """_next_due_delta resolves all label and interval combinations."""

    def _task_with(self, recurring=None, interval_days=None):
        # _next_due_delta only reads these three attributes; a lightweight
        # stand-in avoids SQLAlchemy instrumentation / mapper-config requirements.
        return SimpleNamespace(recurring=recurring, recurring_interval_days=interval_days, due_date=None)

    def _delta(self, recurring=None, interval_days=None) -> timedelta | None:
        from app.commercial.task_routes import _next_due_delta
        return _next_due_delta(self._task_with(recurring, interval_days))

    def test_interval_days_takes_priority(self):
        assert self._delta(recurring="monthly", interval_days=2) == timedelta(days=2)

    def test_daily_label(self):
        assert self._delta(recurring="daily") == timedelta(days=1)

    def test_every_2_days(self):
        assert self._delta(recurring="every_2_days") == timedelta(days=2)

    def test_every_3_days(self):
        assert self._delta(recurring="every_3_days") == timedelta(days=3)

    def test_weekly(self):
        assert self._delta(recurring="weekly") == timedelta(weeks=1)

    def test_biweekly(self):
        assert self._delta(recurring="biweekly") == timedelta(weeks=2)

    def test_monthly(self):
        assert self._delta(recurring="monthly") == timedelta(days=30)

    def test_generic_every_n_days_pattern(self):
        assert self._delta(recurring="every_5_days") == timedelta(days=5)

    def test_none_when_no_recurrence(self):
        assert self._delta() is None

    def test_zero_interval_days_returns_none(self):
        assert self._delta(interval_days=0) is None


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests for _interval_to_label (no DB required)
# ─────────────────────────────────────────────────────────────────────────────


class TestIntervalToLabel:
    def _label(self, days: int):
        from app.scheduler.task_generator import _interval_to_label
        return _interval_to_label(days)

    def test_daily(self):
        assert self._label(1) == "daily"

    def test_weekly(self):
        assert self._label(7) == "weekly"

    def test_biweekly(self):
        assert self._label(14) == "biweekly"

    def test_monthly(self):
        assert self._label(30) == "monthly"

    def test_every_2_days(self):
        assert self._label(2) == "every_2_days"

    def test_every_90_days(self):
        assert self._label(90) == "every_90_days"

    def test_zero_returns_none(self):
        assert self._label(0) is None


# ─────────────────────────────────────────────────────────────────────────────
# Integration: complete_task — roll-forward recurrence
# ─────────────────────────────────────────────────────────────────────────────


class TestCompleteTaskRecurrence:
    async def test_overdue_completion_rolls_forward(self, client, commercial_tenant):
        """Completing an overdue recurring task sets next due in the future."""
        create = await client.post(
            "/v1/tasks",
            json={
                "title": "Daily check",
                "recurring": "daily",
                "due_date": "2020-01-01T07:00:00Z",  # well in the past
            },
            headers=commercial_tenant["headers"],
        )
        assert create.status_code == 201
        task_id = create.json()["id"]

        await client.post(f"/v1/tasks/{task_id}/complete", headers=commercial_tenant["headers"])

        # The spawned next occurrence should have a future due date
        resp = await client.get("/v1/tasks?status=pending", headers=commercial_tenant["headers"])
        pending = [t for t in resp.json()["items"] if t["title"] == "Daily check"]
        assert pending, "Expected a next recurring occurrence"
        next_due = datetime.fromisoformat(pending[0]["due_date"])
        assert next_due > datetime.now(UTC), "Next occurrence must be in the future"

    async def test_every_2_days_respawns(self, client, commercial_tenant):
        """every_2_days recurrence now respawns (previously broken)."""
        create = await client.post(
            "/v1/tasks",
            json={
                "title": "BiDay check",
                "recurring": "every_2_days",
                "due_date": datetime.now(UTC).isoformat(),
            },
            headers=commercial_tenant["headers"],
        )
        task_id = create.json()["id"]
        await client.post(f"/v1/tasks/{task_id}/complete", headers=commercial_tenant["headers"])

        resp = await client.get("/v1/tasks?status=pending", headers=commercial_tenant["headers"])
        pending = [t for t in resp.json()["items"] if t["title"] == "BiDay check"]
        assert pending, "every_2_days should spawn next occurrence"
        next_due = datetime.fromisoformat(pending[0]["due_date"])
        assert next_due > datetime.now(UTC)

    async def test_non_recurring_does_not_spawn(self, client, commercial_tenant):
        """Completing a one-off task creates no next occurrence."""
        create = await client.post(
            "/v1/tasks",
            json={"title": "One-shot task"},
            headers=commercial_tenant["headers"],
        )
        task_id = create.json()["id"]
        await client.post(f"/v1/tasks/{task_id}/complete", headers=commercial_tenant["headers"])

        resp = await client.get("/v1/tasks?status=pending", headers=commercial_tenant["headers"])
        spawned = [t for t in resp.json()["items"] if t["title"] == "One-shot task"]
        assert not spawned, "One-off task should not spawn next occurrence"

    async def test_recurring_interval_days_stored_on_spawn(self, client, commercial_tenant):
        """Spawned occurrence preserves recurring_interval_days."""
        create = await client.post(
            "/v1/tasks",
            json={
                "title": "Interval test",
                "recurring": "every_3_days",
                "due_date": datetime.now(UTC).isoformat(),
            },
            headers=commercial_tenant["headers"],
        )
        # Manually patch interval_days via PATCH since create doesn't expose it
        task_id = create.json()["id"]
        # Simulate seed that has recurring_interval_days=3 set by generator
        from app.commercial.models import Task
        from app.database import async_session_factory
        async with async_session_factory() as session:
            from uuid import UUID
            t = await session.get(Task, UUID(task_id))
            if t:
                t.recurring_interval_days = 3
                await session.commit()

        await client.post(f"/v1/tasks/{task_id}/complete", headers=commercial_tenant["headers"])

        resp = await client.get("/v1/tasks?status=pending", headers=commercial_tenant["headers"])
        pending = [t for t in resp.json()["items"] if t["title"] == "Interval test"]
        assert pending
        assert pending[0]["recurring_interval_days"] == 3


# ─────────────────────────────────────────────────────────────────────────────
# Integration: skip action
# ─────────────────────────────────────────────────────────────────────────────


class TestSkipTask:
    async def test_skip_advances_without_completing(self, client, commercial_tenant):
        """Skipping a recurring task advances to the next occurrence without marking completed."""
        create = await client.post(
            "/v1/tasks",
            json={
                "title": "Skip me",
                "recurring": "daily",
                "due_date": datetime.now(UTC).isoformat(),
            },
            headers=commercial_tenant["headers"],
        )
        assert create.status_code == 201
        task_id = create.json()["id"]

        resp = await client.post(f"/v1/tasks/{task_id}/skip", headers=commercial_tenant["headers"])
        assert resp.status_code == 200
        assert resp.json()["skipped"] is True
        assert resp.json()["next_due"] is not None

        # Skipped task should NOT appear in completed history
        completed = await client.get("/v1/tasks?status=completed", headers=commercial_tenant["headers"])
        assert not any(t["id"] == task_id for t in completed.json()["items"])

        # Next occurrence should exist
        pending = await client.get("/v1/tasks?status=pending", headers=commercial_tenant["headers"])
        next_occs = [t for t in pending.json()["items"] if t["title"] == "Skip me"]
        assert next_occs, "Skip should spawn next occurrence"
        assert next_occs[0]["id"] != task_id

    async def test_skip_404_for_missing_task(self, client, commercial_tenant):
        resp = await client.post(f"/v1/tasks/{uuid4()}/skip", headers=commercial_tenant["headers"])
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Integration: routine-grouped endpoint
# ─────────────────────────────────────────────────────────────────────────────


class TestRoutineGrouped:
    async def _create_grow(self, client, tenant):
        """Create a minimal grow for routine tests."""
        tent = await client.post(
            "/v1/tents",
            json={"name": "Test Tent", "environment_type": "indoor", "size_sqft": 16},
            headers=tenant["headers"],
        )
        grow = await client.post(
            "/v1/grows",
            json={
                "name": "Routine Test Grow",
                "grow_type": "dwc",
                "stage": "vegetative",
                "tent_id": tent.json()["id"],
            },
            headers=tenant["headers"],
        )
        return grow.json()["id"]

    async def test_routines_endpoint_groups_by_routine(self, client, commercial_tenant):
        """Routine endpoint returns tasks grouped, with totals."""
        grow_id = await self._create_grow(client, commercial_tenant)
        now = datetime.now(UTC).isoformat()

        # Create two morning tasks and one evening task
        for i in range(2):
            await client.post(
                "/v1/tasks",
                json={
                    "title": f"Morning task {i}",
                    "grow_cycle_id": grow_id,
                    "due_date": now,
                    "routine": "morning" if True else None,
                },
                headers=commercial_tenant["headers"],
            )
            # Manually set routine since create doesn't expose it
        from uuid import UUID

        from sqlalchemy import select

        from app.commercial.models import Task
        from app.database import async_session_factory
        async with async_session_factory() as session:
            result = await session.execute(
                select(Task).where(
                    Task.title.in_(["Morning task 0", "Morning task 1"]),
                    Task.grow_cycle_id == UUID(grow_id),
                )
            )
            tasks = result.scalars().all()
            for t in tasks:
                t.routine = "morning"
                t.estimated_minutes = 5
            await session.commit()

        resp = await client.get(
            f"/v1/tasks/routines?grow_cycle_id={grow_id}",
            headers=commercial_tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "routines" in data
        morning = next((r for r in data["routines"] if r["routine"] == "morning"), None)
        assert morning is not None
        assert morning["task_count"] >= 2
        assert morning["estimated_minutes"] >= 10  # 2 x 5 min

    async def test_routines_empty_when_no_tasks_today(self, client, commercial_tenant):
        """Routines endpoint returns empty list when no tasks are due today."""
        grow_id = await self._create_grow(client, commercial_tenant)
        far_future = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        await client.post(
            "/v1/tasks",
            json={"title": "Future task", "grow_cycle_id": grow_id, "due_date": far_future},
            headers=commercial_tenant["headers"],
        )

        resp = await client.get(
            f"/v1/tasks/routines?grow_cycle_id={grow_id}",
            headers=commercial_tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["routines"] == []


# ─────────────────────────────────────────────────────────────────────────────
# Unit: generator seed idempotency (without DB — mocks)
# ─────────────────────────────────────────────────────────────────────────────


class TestGeneratorSeedIdempotency:
    """_open_seed_exists prevents duplicate seeds on repeated generation runs."""

    async def test_open_seed_exists_returns_false_for_empty(self, db_session):
        from uuid import uuid4

        from app.scheduler.task_generator import _open_seed_exists
        result = await _open_seed_exists(db_session, uuid4(), "ph_check", uuid4())
        assert result is False

    async def test_open_seed_exists_true_for_pending(self, db_session, commercial_tenant):
        """Inserted pending auto task is detected as an open seed."""
        from app.commercial.models import Task
        from app.grows.models import GrowCycle, Tent
        from app.scheduler.task_generator import _open_seed_exists

        tid = commercial_tenant["tenant"].id
        uid = commercial_tenant["user"].id
        tent = Tent(tenant_id=tid, name="Seed Tent")
        db_session.add(tent)
        await db_session.flush()
        grow = GrowCycle(tenant_id=tid, tent_id=tent.id, name="Seed Grow", grow_type="dwc", stage="vegetative")
        db_session.add(grow)
        await db_session.flush()
        gid = grow.id

        task = Task(
            tenant_id=tid,
            title="Test seed",
            source="auto",
            status="pending",
            priority="medium",
            category="ph_check",
            created_by=uid,
            grow_cycle_id=gid,
        )
        db_session.add(task)
        await db_session.flush()

        exists = await _open_seed_exists(db_session, tid, "ph_check", gid)
        assert exists is True

    async def test_open_seed_exists_false_for_cancelled(self, db_session, commercial_tenant):
        """Cancelled auto tasks are NOT treated as tombstones (unlike old _task_exists)."""
        from app.commercial.models import Task
        from app.grows.models import GrowCycle, Tent
        from app.scheduler.task_generator import _open_seed_exists

        tid = commercial_tenant["tenant"].id
        uid = commercial_tenant["user"].id
        tent = Tent(tenant_id=tid, name="Cancelled Tent")
        db_session.add(tent)
        await db_session.flush()
        grow = GrowCycle(tenant_id=tid, tent_id=tent.id, name="Cancelled Grow", grow_type="dwc", stage="vegetative")
        db_session.add(grow)
        await db_session.flush()
        gid = grow.id

        task = Task(
            tenant_id=tid,
            title="Cancelled seed",
            source="auto",
            status="cancelled",
            priority="medium",
            category="ec_check",
            created_by=uid,
            grow_cycle_id=gid,
        )
        db_session.add(task)
        await db_session.flush()

        exists = await _open_seed_exists(db_session, tid, "ec_check", gid)
        assert exists is False
