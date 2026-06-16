"""Shared retry/backoff for integration connector HTTP calls.

Why
---
Every connector (vivosun, tuya, ecowitt, home_assistant, opensprinkler,
openweather, pulse) makes outbound HTTP calls to third-party clouds.
A single transient failure today \u2014 connection reset, 502 from a
provider's CDN, momentary DNS hiccup \u2014 ends a poll cycle with an
error and the user sees stale data until the next scheduler tick.

This module provides one tested helper, ``retry_request``, that wraps a
single ``httpx`` request in an exponential-backoff-with-jitter loop.
Connectors opt in per-call so they keep full control over which calls
are idempotent enough to retry.

What gets retried
-----------------
* ``httpx.ConnectError`` \u2014 TCP refusal, DNS failure
* ``httpx.ReadTimeout`` / ``httpx.ConnectTimeout`` / ``httpx.WriteTimeout``
* ``httpx.RemoteProtocolError`` \u2014 mid-response disconnect
* 5xx HTTP status (server-side, idempotent enough for GETs)
* 429 Too Many Requests, honouring a ``Retry-After`` header when present
  (capped at ``_MAX_RETRY_AFTER_SECONDS`` to avoid pathological waits)

What does NOT get retried
-------------------------
* 4xx other than 429 \u2014 the request itself is wrong, retrying won't help
* ``asyncio.CancelledError`` \u2014 we honour cooperative cancellation
* Any exception not in the retry list above \u2014 we propagate it
"""

from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable

import httpx

logger = logging.getLogger("tendril.integrations.retry")

# Tuned for third-party SaaS clouds (Vivosun, Tuya, etc.) that occasionally
# 502 for ~30s during their own deploys. 3 attempts at 1s/2s/4s base spans
# the common transient-error window without blocking the scheduler tick.
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY_SECONDS = 1.0
DEFAULT_MAX_DELAY_SECONDS = 8.0
_MAX_RETRY_AFTER_SECONDS = 30.0


_RETRYABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.RemoteProtocolError,
)


def _is_retryable_status(status_code: int) -> bool:
    """5xx and 429 are worth a retry; everything else is the caller's bug."""
    return status_code >= 500 or status_code == 429


def _retry_after(response: httpx.Response) -> float | None:
    """Parse the standard ``Retry-After`` header (seconds form only).

    Some clouds also use HTTP-date form; we treat that as 'no hint' rather
    than try to parse it \u2014 the backoff schedule already has us covered.
    """
    raw = response.headers.get("retry-after")
    if not raw:
        return None
    try:
        seconds = float(raw)
    except ValueError:
        return None
    if seconds <= 0:
        return None
    return min(seconds, _MAX_RETRY_AFTER_SECONDS)


def _compute_delay(attempt: int, base: float, cap: float) -> float:
    """Exponential backoff with full jitter.

    ``attempt`` is 0-indexed: 0 \u2192 [0, base), 1 \u2192 [0, 2\u00d7base), \u2026

    Full jitter (as opposed to equal jitter) eliminates the herd
    problem when multiple workers retry the same upstream endpoint
    simultaneously after a shared outage.
    """
    exp = min(base * (2**attempt), cap)
    return random.uniform(0, exp)  # noqa: S311 \u2014 jitter, not crypto


async def retry_request(
    send: Callable[[], Awaitable[httpx.Response]],
    *,
    description: str,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    base_delay_seconds: float = DEFAULT_BASE_DELAY_SECONDS,
    max_delay_seconds: float = DEFAULT_MAX_DELAY_SECONDS,
) -> httpx.Response:
    """Run ``send`` with exponential-backoff retry on transient failures.

    Callers pass a zero-argument coroutine factory \u2014 typically a
    ``lambda: client.post(url, json=body)`` \u2014 so the *full* request
    can be retried, not just the response read.

    Returns the final response (may still be a 5xx if all attempts
    failed). Raises the final exception if every attempt raised.

    Parameters
    ----------
    send
        Zero-arg coroutine factory producing a single ``httpx.Response``.
    description
        Short identifier for log lines, e.g. ``"vivosun.list_devices"``.
    max_attempts, base_delay_seconds, max_delay_seconds
        Tuning knobs; see module docstring for defaults.
    """
    last_exc: BaseException | None = None
    last_response: httpx.Response | None = None

    for attempt in range(max_attempts):
        try:
            response = await send()
        except _RETRYABLE_EXCEPTIONS as exc:
            last_exc = exc
            last_response = None
            if attempt + 1 >= max_attempts:
                logger.warning(
                    "%s: giving up after %d attempts (%s: %s)",
                    description,
                    max_attempts,
                    type(exc).__name__,
                    exc,
                )
                raise
            delay = _compute_delay(attempt, base_delay_seconds, max_delay_seconds)
            logger.info(
                "%s: transient %s on attempt %d/%d; retrying in %.2fs",
                description,
                type(exc).__name__,
                attempt + 1,
                max_attempts,
                delay,
            )
            await asyncio.sleep(delay)
            continue

        if not _is_retryable_status(response.status_code):
            return response

        last_response = response
        last_exc = None
        if attempt + 1 >= max_attempts:
            logger.warning(
                "%s: giving up after %d attempts (final status %d)",
                description,
                max_attempts,
                response.status_code,
            )
            return response

        retry_after = _retry_after(response)
        delay = (
            retry_after if retry_after is not None else _compute_delay(attempt, base_delay_seconds, max_delay_seconds)
        )
        logger.info(
            "%s: status %d on attempt %d/%d; retrying in %.2fs",
            description,
            response.status_code,
            attempt + 1,
            max_attempts,
            delay,
        )
        await asyncio.sleep(delay)

    # Unreachable under the loop semantics above, but mypy can't tell.
    if last_response is not None:
        return last_response
    assert last_exc is not None
    raise last_exc
