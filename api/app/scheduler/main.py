"""Tendril Scheduler — background task runner.

Runs as a single-replica pod with leader election.
Tasks: health checks (12h), alert evaluation, data retention, daily reports,
weather polling (30min for outdoor tents).
"""
from __future__ import annotations

import asyncio
import logging
import signal

from app.config import get_settings
from app.scheduler.tasks import TaskRunner

logger = logging.getLogger("tendril.scheduler")


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
    logger.info("Tendril Scheduler starting")

    shutdown_event = asyncio.Event()

    def _signal_handler():
        logger.info("Shutdown signal received")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    # Leader election — only the leader runs tasks
    from app.database import async_session_factory
    from app.scheduler.leader import try_acquire_leader, release_leader

    async with async_session_factory() as session:
        is_leader = await try_acquire_leader(session)
        if not is_leader:
            logger.info("Not elected leader — waiting for lock")
            # Retry every 30s until we become leader or shutdown
            while not shutdown_event.is_set() and not is_leader:
                try:
                    await asyncio.wait_for(shutdown_event.wait(), timeout=30)
                    break
                except asyncio.TimeoutError:
                    is_leader = await try_acquire_leader(session)

        if is_leader and not shutdown_event.is_set():
            logger.info("Elected as scheduler leader — starting tasks")
            try:
                runner = TaskRunner(settings)
                await runner.run(shutdown_event)
            finally:
                await release_leader(session)

    logger.info("Tendril Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
