"""Request logging middleware — structured access logs with correlation IDs."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import request_id_var

logger = logging.getLogger("tendril.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with timing, correlation ID, and tenant context."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        rid = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request_id_var.set(rid)

        start = time.perf_counter()
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
            request.client.host if request.client else "-"
        )
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            if request.url.path != "/health":
                logger.exception(
                    "%s %s failed %.1fms",
                    request.method,
                    request.url.path,
                    duration_ms,
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": 500,
                        "duration_ms": duration_ms,
                        "ip": ip,
                        "action": "http_request",
                        "outcome": "error",
                    },
                )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        # Inject correlation header into response
        response.headers["X-Request-ID"] = rid

        # Skip health checks from access log
        if request.url.path == "/health":
            return response

        logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "ip": ip,
                "action": "http_request",
                "outcome": "success" if response.status_code < 500 else "error",
            },
        )

        return response
