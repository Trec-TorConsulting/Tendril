"""Scheduler health HTTP server — lightweight endpoint for Kubernetes probes.

Runs on port 8080 inside the scheduler pod.
- GET /healthz → liveness (always 200 if process is alive)
- GET /readyz → readiness (200 if leader + tasks running)
- GET /metrics → Prometheus text format
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from aiohttp import web
from prometheus_client import Counter, Gauge, generate_latest

logger = logging.getLogger("tendril.scheduler.health")

# Prometheus metrics
TASK_LAST_RUN = Gauge(
    "tendril_scheduler_last_task_run_timestamp",
    "Unix timestamp of last successful task execution",
)
TASK_ERRORS = Counter(
    "tendril_scheduler_task_errors_total",
    "Total task execution errors",
    ["task"],
)
LEADER_STATUS = Gauge(
    "tendril_scheduler_is_leader",
    "Whether this instance is the elected leader (1=yes, 0=no)",
)

# Global state updated by the task runner
_state: dict[str, bool | datetime | None] = {
    "is_leader": False,
    "last_task_run": None,
    "started_at": None,
}


def set_leader(is_leader: bool) -> None:
    _state["is_leader"] = is_leader
    LEADER_STATUS.set(1 if is_leader else 0)


def record_task_run() -> None:
    _state["last_task_run"] = datetime.now(UTC)
    TASK_LAST_RUN.set_to_current_time()


def record_task_error(task_name: str) -> None:
    TASK_ERRORS.labels(task=task_name).inc()


async def _healthz(request: web.Request) -> web.Response:
    """Liveness probe — returns 200 if process is alive."""
    return web.json_response({"status": "ok", "service": "scheduler"})


async def _readyz(request: web.Request) -> web.Response:
    """Readiness probe — returns 200 if elected leader and running tasks."""
    if not _state["is_leader"]:
        return web.json_response(
            {"status": "not_ready", "reason": "not_leader"},
            status=503,
        )
    return web.json_response(
        {
            "status": "ready",
            "is_leader": True,
            "last_task_run": (
                _state["last_task_run"].isoformat()
                if isinstance(_state["last_task_run"], datetime)
                else None
            ),
            "started_at": (
                _state["started_at"].isoformat()
                if isinstance(_state["started_at"], datetime)
                else None
            ),
        }
    )


async def _metrics(request: web.Request) -> web.Response:
    """Prometheus metrics endpoint."""
    return web.Response(
        body=generate_latest(),
        content_type="text/plain; version=0.0.4; charset=utf-8",
    )


async def start_health_server() -> None:
    """Start the health HTTP server on port 8080."""
    _state["started_at"] = datetime.now(UTC)
    app = web.Application()
    app.router.add_get("/healthz", _healthz)
    app.router.add_get("/readyz", _readyz)
    app.router.add_get("/metrics", _metrics)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)  # nosec B104 — container-only
    await site.start()
    logger.info("Scheduler health server listening on :8080")
