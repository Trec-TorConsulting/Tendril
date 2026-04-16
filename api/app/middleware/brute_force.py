"""Account lockout and brute-force protection middleware."""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

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

    MAX_ATTEMPTS = 5
    WINDOW = 300        # 5 minutes
    LOCKOUT = 900       # 15 minutes
    LOGIN_PATHS = {"/v1/auth/login", "/v1/auth/token"}

    def __init__(self, app):
        super().__init__(app)
        self._attempts: dict[str, LoginAttempts] = defaultdict(LoginAttempts)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path not in self.LOGIN_PATHS or request.method != "POST":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        record = self._attempts[client_ip]
        now = time.monotonic()

        # Check lockout
        if record.locked_until > now:
            remaining = int(record.locked_until - now)
            return JSONResponse(
                status_code=429,
                content={"detail": f"Too many login attempts. Try again in {remaining}s."},
                headers={"Retry-After": str(remaining)},
            )

        response = await call_next(request)

        # Track failed attempts
        if response.status_code in (401, 403):
            if now - record.first_attempt > self.WINDOW:
                record.count = 0
                record.first_attempt = now
            record.count += 1
            if record.count >= self.MAX_ATTEMPTS:
                record.locked_until = now + self.LOCKOUT
                record.count = 0
        elif response.status_code == 200:
            # Successful login resets counter
            record.count = 0
            record.locked_until = 0

        return response
