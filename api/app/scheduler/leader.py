"""Scheduler leader election for single-active-instance guarantee.

Uses PostgreSQL advisory locks for leader election.
Only the pod holding the lock runs scheduled tasks.
"""
from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("tendril.scheduler.leader")

# Arbitrary lock ID for scheduler leader election
LEADER_LOCK_ID = 999_001


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


async def release_leader(session: AsyncSession) -> None:
    """Release the advisory lock."""
    await session.execute(
        text("SELECT pg_advisory_unlock(:lock_id)"),
        {"lock_id": LEADER_LOCK_ID},
    )
    logger.info("Released scheduler leader lock")
