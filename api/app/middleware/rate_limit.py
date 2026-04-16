"""Rate limiting middleware — per-tenant and per-IP."""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


@dataclass
class RateBucket:
    tokens: float
    last_refill: float


class RateLimiter(BaseHTTPMiddleware):
    """Token bucket rate limiter.

    Limits:
    - Per-IP: 60 requests/minute for unauthenticated
    - Per-tenant: 300 requests/minute for authenticated
    - Stripe webhooks and health checks are exempt
    """

    EXEMPT_PATHS = {"/health", "/v1/billing/webhook"}

    def __init__(self, app, ip_rate: int = 60, tenant_rate: int = 300, window: int = 60):
        super().__init__(app)
        self.ip_rate = ip_rate
        self.tenant_rate = tenant_rate
        self.window = window
        self._ip_buckets: dict[str, RateBucket] = defaultdict(
            lambda: RateBucket(tokens=ip_rate, last_refill=time.monotonic())
        )
        self._tenant_buckets: dict[str, RateBucket] = defaultdict(
            lambda: RateBucket(tokens=tenant_rate, last_refill=time.monotonic())
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Identify client
        client_ip = request.client.host if request.client else "unknown"
        tenant_id = None

        # Check for tenant from Authorization header (JWT)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.auth.jwt import decode_token
                payload = decode_token(auth_header[7:])
                tenant_id = payload.get("tid")
            except Exception:
                pass

        # Check rate limit
        if tenant_id:
            if not self._check_bucket(self._tenant_buckets[tenant_id], self.tenant_rate):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={"Retry-After": str(self.window)},
                )
        else:
            if not self._check_bucket(self._ip_buckets[client_ip], self.ip_rate):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={"Retry-After": str(self.window)},
                )

        return await call_next(request)

    def _check_bucket(self, bucket: RateBucket, max_tokens: int) -> bool:
        now = time.monotonic()
        elapsed = now - bucket.last_refill
        bucket.tokens = min(max_tokens, bucket.tokens + elapsed * (max_tokens / self.window))
        bucket.last_refill = now

        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False
