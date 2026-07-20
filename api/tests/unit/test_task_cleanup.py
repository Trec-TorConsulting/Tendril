"""Tests for the one-time cleanup-and-regenerate script.

Verifies the DELETE side of cleanup_and_regen_tasks without needing a full
async scheduler run. The generator's regen path is tested via seed idempotency
tests; here we focus on what gets deleted and what is preserved.

Note: automation_suppressions and stage_transition_tasks tables do NOT exist
in the test DB (create_all vs Alembic). Tests assert on the DELETE behaviour
and handle generator failures gracefully.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy import select

from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def cleanup_tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create(plan="commercial")


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────


async def _seed_tasks(session, tenant_id, user_id, grow_id=None, *, active_grow_id=None, past_grow_id=None):
    """Insert a mix of tasks covering all preservation cases."""
    from app.commercial.models import Task

    rows = [
        # Should be DELETED: open auto tasks on active grow
        Task(tenant_id=tenant_id, title="auto-pending-active", source="auto", status="pending",
             priority="medium", created_by=user_id, grow_cycle_id=active_grow_id),
        Task(tenant_id=tenant_id, title="auto-inprog-active", source="auto", status="in_progress",
             priority="medium", created_by=user_id, grow_cycle_id=active_grow_id),
        # Should be DELETED: open auto tasks on past grow
        Task(tenant_id=tenant_id, title="auto-pending-past", source="auto", status="pending",
             priority="medium", created_by=user_id, grow_cycle_id=past_grow_id),
        # Should be DELETED: open auto task with null grow_cycle_id
        Task(tenant_id=tenant_id, title="auto-pending-null-grow", source="auto", status="pending",
             priority="medium", created_by=user_id, grow_cycle_id=None),
        # Should be PRESERVED: completed auto task
        Task(tenant_id=tenant_id, title="auto-completed", source="auto", status="completed",
             priority="medium", created_by=user_id, grow_cycle_id=active_grow_id,
             completed_at=datetime.now(UTC)),
        # Should be PRESERVED: cancelled auto task
        Task(tenant_id=tenant_id, title="auto-cancelled", source="auto", status="cancelled",
             priority="medium", created_by=user_id, grow_cycle_id=active_grow_id),
        # Should be PRESERVED: manual task
        Task(tenant_id=tenant_id, title="manual-pending", source="manual", status="pending",
             priority="medium", created_by=user_id, grow_cycle_id=active_grow_id),
        # Should be PRESERVED: AI task
        Task(tenant_id=tenant_id, title="ai-pending", source="ai", status="pending",
             priority="medium", created_by=user_id, grow_cycle_id=active_grow_id),
    ]
    for row in rows:
        session.add(row)
    await session.flush()
    return rows


class TestCleanupScript:
    async def test_deletes_open_auto_tasks_all_grows(self, client, cleanup_tenant, db_session):
        """Open auto tasks are removed for active, past, and null-grow rows."""
        from sqlalchemy import select

        from app.commercial.models import Task
        from app.database import async_session_factory
        from app.grows.models import GrowCycle, Tent

        tenant_id = cleanup_tenant["tenant"].id
        user_id = cleanup_tenant["user"].id

        # Create two grows: one active, one completed
        tent = Tent(tenant_id=tenant_id, name="Cleanup Tent")
        db_session.add(tent)
        await db_session.flush()
        active_grow = GrowCycle(
            tenant_id=tenant_id,
            tent_id=tent.id,
            name="Active Grow",
            grow_type="dwc",
            stage="vegetative",
            status="active",
        )
        past_grow = GrowCycle(
            tenant_id=tenant_id,
            tent_id=tent.id,
            name="Past Grow",
            grow_type="soil",
            stage="harvest",
            status="completed",
        )
        db_session.add(active_grow)
        db_session.add(past_grow)
        await db_session.flush()

        await _seed_tasks(db_session, tenant_id, user_id,
                          active_grow_id=active_grow.id, past_grow_id=past_grow.id)
        await db_session.commit()

        # Run the cleanup script core logic directly (skip argparse/asyncio.run)
        # Patch generate_tasks_for_grow to no-op (generator needs real tables)
        from scripts.cleanup_and_regen_tasks import _run

        import app.scheduler.task_generator as tg
        original = tg.generate_tasks_for_grow

        async def _noop_regen(session, grow, **kw):
            return 0

        tg.generate_tasks_for_grow = _noop_regen
        try:
            await _run(dry_run=False, tenant_filter=tenant_id, yes=True)
        finally:
            tg.generate_tasks_for_grow = original

        # Verify deletions
        async with async_session_factory() as session:
            result = await session.execute(
                select(Task.title, Task.source, Task.status).where(Task.tenant_id == tenant_id)
            )
            rows = {(r.title, r.source, r.status) for r in result}

        # These should be gone
        assert ("auto-pending-active", "auto", "pending") not in rows
        assert ("auto-inprog-active", "auto", "in_progress") not in rows
        assert ("auto-pending-past", "auto", "pending") not in rows
        assert ("auto-pending-null-grow", "auto", "pending") not in rows

        # These should be preserved
        assert ("auto-completed", "auto", "completed") in rows
        assert ("auto-cancelled", "auto", "cancelled") in rows
        assert ("manual-pending", "manual", "pending") in rows
        assert ("ai-pending", "ai", "pending") in rows

    async def test_dry_run_makes_no_changes(self, client, cleanup_tenant, db_session):
        """Dry-run mode reports counts but writes nothing."""
        from app.commercial.models import Task
        from app.database import async_session_factory

        tenant_id = cleanup_tenant["tenant"].id
        user_id = cleanup_tenant["user"].id

        # Insert a fresh pending auto task
        task = Task(
            tenant_id=tenant_id, title="dry-run-auto", source="auto",
            status="pending", priority="medium", created_by=user_id,
        )
        db_session.add(task)
        await db_session.commit()

        from scripts.cleanup_and_regen_tasks import _run
        await _run(dry_run=True, tenant_filter=tenant_id, yes=True)

        # Task must still exist
        async with async_session_factory() as session:
            result = await session.execute(
                select(Task).where(Task.id == task.id)
            )
            assert result.scalar_one_or_none() is not None

    async def test_idempotent_second_run(self, client, cleanup_tenant, db_session):
        """Running cleanup twice produces no additional changes."""
        from app.commercial.models import Task
        from app.database import async_session_factory

        tenant_id = cleanup_tenant["tenant"].id

        # Ensure a clean state for this tenant (from earlier tests)
        import app.scheduler.task_generator as tg

        async def _noop_regen(session, grow, **kw):
            return 0

        orig = tg.generate_tasks_for_grow
        tg.generate_tasks_for_grow = _noop_regen

        from scripts.cleanup_and_regen_tasks import _run
        try:
            # First run
            await _run(dry_run=False, tenant_filter=tenant_id, yes=True)
            # Second run — should be a no-op
            await _run(dry_run=False, tenant_filter=tenant_id, yes=True)
        finally:
            tg.generate_tasks_for_grow = orig

        # No unexpected task rows should exist as open-auto for this tenant
        async with async_session_factory() as session:
            result = await session.execute(
                select(Task).where(
                    Task.tenant_id == tenant_id,
                    Task.source == "auto",
                    Task.status.in_(["pending", "in_progress"]),
                )
            )
            open_auto = result.scalars().all()
        assert len(open_auto) == 0, "Second run should leave zero open auto tasks"
