"""Rate limiting middleware — per-tenant and per-IP.

Uses Redis when available (multi-instance / K8s) and falls back to
in-memory token buckets for local development.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

import jwt as pyjwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("tendril.middleware.ratelimit")

# Common bot/scanner paths — reject immediately without consuming rate limit
_BOT_PATH_PREFIXES = (
    "/wp-",
    "/xmlrpc",
    "/.env",
    "/config",
    "/admin",
    "/cgi-bin",
    "/vendor",
    "/telescope",
    "/debug",
    "/actuator",
    "/solr",
    "/.git",
    "/assets/js/",
    "/static/style/",
    "/js/",
    "/css/support",
    "/bot-connect",
)


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
    - Bot scanner paths are rejected immediately
    """

    EXEMPT_PATHS = {"/health", "/v1/billing/webhook"}

    def __init__(self, app, ip_rate: int | None = None, tenant_rate: int | None = None, window: int = 60):
        import os

        ip_rate = ip_rate or int(os.environ.get("RATE_LIMIT_IP", "60"))
        tenant_rate = tenant_rate or int(os.environ.get("RATE_LIMIT_TENANT", "300"))
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

    @staticmethod
    def _get_real_ip(request: Request) -> str:
        """Extract the real client IP from proxy headers."""
        # X-Forwarded-For: client, proxy1, proxy2
        forwarded_for = request.headers.get("x-forwarded-for", "")
        if forwarded_for:
            # First IP in the chain is the original client
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip", "")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "unknown"

    @staticmethod
    def _extract_tenant_id(request: Request) -> str | None:
        """Extract tenant_id from Bearer token or session cookie.

        Uses options={"verify_exp": False} so that expired access tokens
        still route to the per-tenant bucket (avoids IP-bucket starvation
        when cookies haven't been refreshed yet).
        """
        from app.config import get_settings

        auth_header = request.headers.get("authorization", "")
        token_str = auth_header[7:] if auth_header.startswith("Bearer ") else request.cookies.get("access_token", "")

        if not token_str:
            return None

        try:
            settings = get_settings()
            payload = pyjwt.decode(
                token_str,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False},
            )
            return payload.get("tid")
        except Exception:
            # Malformed/expired/invalid token — fall back to per-IP limiting.
            logger.debug("rate-limit: could not derive tenant from token", exc_info=True)
            return None

    # ── Dispatch ───────────────────────────────────────────────
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        if path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Block known bot/scanner paths immediately (no rate limit cost)
        if any(path.startswith(prefix) for prefix in _BOT_PATH_PREFIXES):
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        # Identify client by real IP (behind proxy)
        client_ip = self._get_real_ip(request)
        tenant_id = self._extract_tenant_id(request)

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
