"""Account lockout and brute-force protection middleware.

Uses Redis when available (multi-instance / K8s) and falls back to
in-memory tracking for local development.
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from dataclasses import dataclass

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


@dataclass
class LoginAttempts:
    count: int = 0
    first_attempt: float = 0.0
    locked_until: float = 0.0


class BruteForceProtection(BaseHTTPMiddleware):
    """Block IPs after too many failed login attempts.

    5 failed attempts in 5 minutes → 15 minute lockout.
    """

    MAX_ATTEMPTS = int(os.environ.get("BRUTE_FORCE_MAX_ATTEMPTS", "5"))
    WINDOW = 300  # 5 minutes
    LOCKOUT = 900  # 15 minutes
    LOGIN_PATHS = {"/v1/auth/login", "/v1/auth/token"}

    def __init__(self, app):
        super().__init__(app)
        # In-memory fallback
        self._attempts: dict[str, LoginAttempts] = defaultdict(LoginAttempts)

    # ── Redis helpers ──────────────────────────────────────────
    async def _redis_is_locked(self, client_ip: str, redis) -> int | None:
        """Return seconds remaining if locked, else None."""
        locked = await redis.get(f"bf:lock:{client_ip}")
        if locked:
            return int(float(locked) - time.time())
        return None

    async def _redis_record_failure(self, client_ip: str, redis) -> None:
        key = f"bf:fail:{client_ip}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, self.WINDOW)
        if count >= self.MAX_ATTEMPTS:
            await redis.set(f"bf:lock:{client_ip}", str(time.time() + self.LOCKOUT), ex=self.LOCKOUT)
            await redis.delete(key)

    async def _redis_reset(self, client_ip: str, redis) -> None:
        await redis.delete(f"bf:fail:{client_ip}", f"bf:lock:{client_ip}")

    # ── Dispatch ───────────────────────────────────────────────
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path not in self.LOGIN_PATHS or request.method != "POST":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        from app.middleware.redis_store import get_redis

        redis = await get_redis()

        # ── Check lockout ──────────────────────────────────────
        if redis:
            remaining = await self._redis_is_locked(client_ip, redis)
            if remaining and remaining > 0:
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Too many login attempts. Try again in {remaining}s."},
                    headers={"Retry-After": str(remaining)},
                )
        else:
            record = self._attempts[client_ip]
            now = time.monotonic()
            if record.locked_until > now:
                remaining = int(record.locked_until - now)
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Too many login attempts. Try again in {remaining}s."},
                    headers={"Retry-After": str(remaining)},
                )

        response = await call_next(request)

        # ── Track outcome ──────────────────────────────────────
        if response.status_code in (401, 403):
            if redis:
                await self._redis_record_failure(client_ip, redis)
            else:
                now = time.monotonic()
                record = self._attempts[client_ip]
                if now - record.first_attempt > self.WINDOW:
                    record.count = 0
                    record.first_attempt = now
                record.count += 1
                if record.count >= self.MAX_ATTEMPTS:
                    record.locked_until = now + self.LOCKOUT
                    record.count = 0
        elif response.status_code == 200:
            if redis:
                await self._redis_reset(client_ip, redis)
            else:
                record = self._attempts[client_ip]
                record.count = 0
                record.locked_until = 0

        return response
