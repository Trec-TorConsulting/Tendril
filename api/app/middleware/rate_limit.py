"""Rate limiting middleware — per-tenant and per-IP.

Uses Redis when available (multi-instance / K8s) and falls back to
in-memory token buckets for local development.
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

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
        # In-memory fallback
        self._ip_buckets: dict[str, RateBucket] = defaultdict(
            lambda: RateBucket(tokens=ip_rate, last_refill=time.monotonic())
        )
        self._tenant_buckets: dict[str, RateBucket] = defaultdict(
            lambda: RateBucket(tokens=tenant_rate, last_refill=time.monotonic())
        )

    # ── Redis helpers ──────────────────────────────────────────
    async def _redis_check(self, key: str, max_tokens: int, redis) -> bool:
        """Atomic token-bucket check via Redis."""
        lua = """
        local key = KEYS[1]
        local max = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local data = redis.call('HMGET', key, 'tokens', 'ts')
        local tokens = tonumber(data[1]) or max
        local last   = tonumber(data[2]) or now

        local elapsed = now - last
        tokens = math.min(max, tokens + elapsed * (max / window))
        if tokens >= 1 then
            tokens = tokens - 1
            redis.call('HMSET', key, 'tokens', tokens, 'ts', now)
            redis.call('EXPIRE', key, window * 2)
            return 1
        else
            redis.call('HMSET', key, 'tokens', tokens, 'ts', now)
            redis.call('EXPIRE', key, window * 2)
            return 0
        end
        """
        result = await redis.eval(lua, 1, key, max_tokens, self.window, time.time())
        return result == 1

    # ── Dispatch ───────────────────────────────────────────────
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
            except Exception:  # noqa: S110
                pass

        # Try Redis first, fallback to in-memory
        from app.middleware.redis_store import get_redis

        redis = await get_redis()

        if tenant_id:
            if redis:
                allowed = await self._redis_check(f"rl:tenant:{tenant_id}", self.tenant_rate, redis)
            else:
                allowed = self._check_bucket(self._tenant_buckets[tenant_id], self.tenant_rate)
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={"Retry-After": str(self.window)},
                )
        else:
            if redis:
                allowed = await self._redis_check(f"rl:ip:{client_ip}", self.ip_rate, redis)
            else:
                allowed = self._check_bucket(self._ip_buckets[client_ip], self.ip_rate)
            if not allowed:
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
