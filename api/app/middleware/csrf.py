"""CSRF protection middleware — double-submit cookie pattern.

How it works:
1. On auth (login/register), server sets a `csrf_token` cookie (readable by JS, NOT httpOnly).
2. For state-changing requests (POST/PUT/PATCH/DELETE), the client must send
   the same value in the `X-CSRF-Token` header.
3. Middleware compares cookie value vs header value; rejects on mismatch.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Methods that require CSRF validation
_UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Paths exempt from CSRF (auth endpoints that create sessions, webhooks with their own auth)
_CSRF_EXEMPT_PATHS = {
    "/v1/auth/login",
    "/v1/auth/register",
    "/v1/auth/refresh",
    "/v1/auth/forgot-password",
    "/v1/auth/reset-password",
    "/v1/auth/verify-email",
    "/v1/billing/webhook",
    "/v1/integrations/webhook/",
    "/health",
}


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_urlsafe(32)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Validate CSRF tokens on unsafe HTTP methods using double-submit cookie."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in _UNSAFE_METHODS:
            path = request.url.path

            # Skip exempt paths
            if not any(path.startswith(exempt) for exempt in _CSRF_EXEMPT_PATHS):
                cookie_token = request.cookies.get("csrf_token")
                header_token = request.headers.get("x-csrf-token")

                if not cookie_token or not header_token:
                    return Response(
                        content='{"detail":"CSRF token missing"}',
                        status_code=403,
                        media_type="application/json",
                    )

                if not secrets.compare_digest(cookie_token, header_token):
                    return Response(
                        content='{"detail":"CSRF token mismatch"}',
                        status_code=403,
                        media_type="application/json",
                    )

        response = await call_next(request)
        return response
