"""Tenant plan resolution middleware — populates request.state for tier gating."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("tendril.middleware.tenant_plan")

# In-memory plan cache: tenant_id -> (timestamp, plan_slug)
_tenant_plan_cache: dict[str, tuple[float, str]] = {}
_CACHE_TTL = 30.0  # seconds


class TenantPlanMiddleware(BaseHTTPMiddleware):
    """Resolves the tenant's active plan and sets request.state.tenant_plan.

    Reads tenant_id from the JWT (if present) and queries the tenant's plan
    column with a short TTL cache to avoid DB hits on every request.
    """

    SKIP_PATHS = {"/health", "/health/ready", "/v1/billing/webhook"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip non-authenticated paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        tenant_id: str | None = None
        tenant_plan = "free"

        # Extract tenant_id from JWT (cookie or header)
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if token:
            try:
                from app.auth.jwt import decode_token

                payload = decode_token(token)
                tenant_id = payload.get("tid")
            except Exception:  # noqa: S110
                pass  # Invalid token — auth middleware will reject later

        if tenant_id:
            tenant_plan = await _resolve_plan(tenant_id)

        request.state.tenant_id = UUID(tenant_id) if tenant_id else None
        request.state.tenant_plan = tenant_plan

        return await call_next(request)


async def _resolve_plan(tenant_id: str) -> str:
    """Look up tenant plan with in-memory cache."""
    now = time.time()
    cached = _tenant_plan_cache.get(tenant_id)
    if cached and (now - cached[0]) < _CACHE_TTL:
        return cached[1]

    try:
        from sqlalchemy import select

        from app.database import async_session_factory
        from app.tenants.models import Tenant

        async with async_session_factory() as session:
            result = await session.execute(select(Tenant.plan).where(Tenant.id == UUID(tenant_id)))
            plan = result.scalar_one_or_none() or "free"

        _tenant_plan_cache[tenant_id] = (now, plan)
        return plan
    except Exception:
        logger.debug("Failed to resolve plan for tenant %s", tenant_id, exc_info=True)
        return "free"
