"""Scheduler leader election for single-active-instance guarantee.

Uses PostgreSQL advisory locks for leader election.
Only the pod holding the lock runs scheduled tasks.
Includes a heartbeat that re-validates lock ownership every 60s.
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("tendril.scheduler.leader")

# Arbitrary lock ID for scheduler leader election
LEADER_LOCK_ID = 999_001

HEARTBEAT_INTERVAL = 60  # seconds


async def try_acquire_leader(session: AsyncSession) -> bool:
    """Attempt to acquire the advisory lock. Returns True if this instance is leader."""
    result = await session.execute(
        text("SELECT pg_try_advisory_lock(:lock_id)"),
        {"lock_id": LEADER_LOCK_ID},
    )
    row = result.scalar()
    if row:
        logger.info("Acquired scheduler leader lock")
    return bool(row)


async def verify_leader(session: AsyncSession) -> bool:
    """Check if this session still holds the advisory lock."""
    result = await session.execute(
        text(
            "SELECT COUNT(*) FROM pg_locks WHERE locktype = 'advisory' AND objid = :lock_id AND pid = pg_backend_pid()"
        ),
        {"lock_id": LEADER_LOCK_ID},
    )
    return (result.scalar() or 0) > 0


async def run_heartbeat(session: AsyncSession, shutdown_event: asyncio.Event) -> None:
    """Periodically re-validate leadership. Sets shutdown_event on lock loss."""
    while not shutdown_event.is_set():
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=HEARTBEAT_INTERVAL)
            break  # shutdown requested
        except TimeoutError:
            pass

        try:
            still_leader = await verify_leader(session)
        except Exception:
            logger.exception("Heartbeat check failed — assuming lock lost")
            still_leader = False

        if not still_leader:
            logger.error("Leadership lock lost — initiating graceful shutdown")
            shutdown_event.set()
            break

        logger.debug("Heartbeat: leadership confirmed")


async def release_leader(session: AsyncSession) -> None:
    """Release the advisory lock."""
    await session.execute(
        text("SELECT pg_advisory_unlock(:lock_id)"),
        {"lock_id": LEADER_LOCK_ID},
    )
    logger.info("Released scheduler leader lock")
