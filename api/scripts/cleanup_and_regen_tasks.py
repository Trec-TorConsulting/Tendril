"""One-time cross-tenant cleanup and regeneration of auto-generated tasks.

Deletes every open (pending/in_progress) source='auto' task for ALL tenants
and ALL grows (active and past), then regenerates recurring-seed tasks for
active grows only using the new seed-based generator.

Manual, AI, completed, and cancelled tasks are never touched.

Usage
-----
    # Dry run — reports counts without writing anything
    python -m scripts.cleanup_and_regen_tasks --dry-run

    # Scope to one tenant for testing
    python -m scripts.cleanup_and_regen_tasks --tenant <uuid> --yes

    # Full production run (used by the k8s Job)
    python -m scripts.cleanup_and_regen_tasks --yes

Environment
-----------
All config is read from app/config.py.  At minimum DATABASE_URL and JWT_SECRET
must be set (the script never uses JWT, but the Settings dataclass requires it).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from uuid import UUID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("tendril.scripts.cleanup_regen_tasks")


async def _run(*, dry_run: bool, tenant_filter: UUID | None, yes: bool) -> None:
    # Import here so env vars are already in place
    from sqlalchemy import delete, func, select

    from app.commercial.models import Task
    from app.database import async_session_factory
    from app.grows.models import GrowCycle
    from app.scheduler.task_generator import generate_tasks_for_grow

    async with async_session_factory() as session:
        # ── Count what we will delete ─────────────────────────────────────
        count_q = select(func.count()).select_from(Task).where(
            Task.source == "auto",
            Task.status.in_(["pending", "in_progress"]),
        )
        if tenant_filter:
            count_q = count_q.where(Task.tenant_id == tenant_filter)

        total_to_delete: int = (await session.execute(count_q)).scalar_one()

        # ── Count active grows to regenerate ─────────────────────────────
        grows_q = select(GrowCycle).where(GrowCycle.status == "active")
        if tenant_filter:
            grows_q = grows_q.where(GrowCycle.tenant_id == tenant_filter)
        active_grows = (await session.execute(grows_q)).scalars().all()

        logger.info(
            "DRY-RUN=%s | open auto tasks to delete: %d | active grows to regen: %d",
            dry_run,
            total_to_delete,
            len(active_grows),
        )

        if dry_run:
            logger.info("Dry-run complete — no changes written.")
            return

        if not yes:
            sys.stderr.write(
                f"\nAbout to DELETE {total_to_delete} open auto tasks and regenerate "
                f"{len(active_grows)} active grows.\n"
                "Pass --yes to proceed.\n"
            )
            sys.exit(1)

        # ── Step 1: Delete open auto tasks (commit BEFORE regen) ─────────
        del_q = delete(Task).where(
            Task.source == "auto",
            Task.status.in_(["pending", "in_progress"]),
        )
        if tenant_filter:
            del_q = del_q.where(Task.tenant_id == tenant_filter)

        result = await session.execute(del_q)
        deleted: int = result.rowcount or 0
        await session.commit()  # commit delete first so _task_exists tombstones are gone
        logger.info("Deleted %d open auto tasks.", deleted)

    # ── Step 2: Regenerate seeds for active grows ─────────────────────
    # Use a fresh session per tenant batch for bounded transaction size.
    errors = 0
    total_created = 0
    grows_processed = 0

    # Group grows by tenant so we can commit per-tenant
    from collections import defaultdict
    grows_by_tenant: dict[UUID, list[GrowCycle]] = defaultdict(list)
    for grow in active_grows:
        grows_by_tenant[grow.tenant_id].append(grow)

    for tenant_id, tenant_grows in grows_by_tenant.items():
        async with async_session_factory() as session:
            for grow in tenant_grows:
                try:
                    count = await generate_tasks_for_grow(session, grow)
                    total_created += count
                    grows_processed += 1
                except Exception:
                    logger.exception(
                        "Regen failed for grow %s (tenant %s) — continuing",
                        grow.id,
                        tenant_id,
                    )
                    errors += 1
                    await session.rollback()
                    continue
            try:
                await session.commit()
            except Exception:
                logger.exception("Commit failed for tenant %s batch — skipping", tenant_id)
                await session.rollback()
                errors += 1

    logger.info(
        "Done. deleted=%d | grows_processed=%d | tasks_created=%d | errors=%d",
        deleted,
        grows_processed,
        total_created,
        errors,
    )
    if errors:
        logger.warning("%d error(s) occurred — check logs above for details.", errors)
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean up materialized auto-tasks and regenerate recurring seeds."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report counts without writing any changes.",
    )
    parser.add_argument(
        "--tenant",
        metavar="UUID",
        help="Scope operation to a single tenant UUID (for staged rollout / testing).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (required for non-interactive / k8s Job use).",
    )
    args = parser.parse_args()

    tenant_filter: UUID | None = None
    if args.tenant:
        try:
            tenant_filter = UUID(args.tenant)
        except ValueError:
            sys.stderr.write(f"Invalid tenant UUID: {args.tenant}\n")
            sys.exit(1)

    asyncio.run(_run(dry_run=args.dry_run, tenant_filter=tenant_filter, yes=args.yes))


if __name__ == "__main__":
    main()
