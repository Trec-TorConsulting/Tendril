"""Alert dedup/suppression with Redis TTL + in-memory fallback.

Prevents alert spam by suppressing repeat firings of the same
``(tenant, rule, device)`` bucket within a configurable window.

The window is controlled by ``ALERT_SUPPRESSION_MINUTES`` (default 30).

Storage:
- Redis (preferred): ``SET key 1 EX ttl`` — self-evicting, shared across
  workers.
- In-process dict (fallback): used only when Redis is unavailable
  (typically local dev / tests). Loses state on restart, which is fine
  for those environments.
"""

from __future__ import annotations

import logging
import os
import time

from app.middleware.redis_store import get_redis

logger = logging.getLogger("tendril.automation.suppression")

# In-process fallback: key -> unix expiry timestamp (monotonic-ish via time.time)
_memory: dict[str, float] = {}


def _window_seconds() -> int:
    return int(os.environ.get("ALERT_SUPPRESSION_MINUTES", "30")) * 60


def _key(tenant_id: object, rule_id: object, device_id: object) -> str:
    return f"alert:suppress:{tenant_id}:{rule_id}:{device_id}"


async def is_suppressed(tenant_id: object, rule_id: object, device_id: object) -> bool:
    """Return True if ``(tenant, rule, device)`` has fired within the window."""
    key = _key(tenant_id, rule_id, device_id)
    redis = await get_redis()
    if redis is not None:
        try:
            return bool(await redis.exists(key))
        except Exception:
            logger.warning("Redis EXISTS failed for %s; falling back to memory", key)

    now = time.time()
    expiry = _memory.get(key)
    if expiry is None:
        return False
    if expiry < now:
        _memory.pop(key, None)
        return False
    return True


async def mark_fired(tenant_id: object, rule_id: object, device_id: object) -> None:
    """Mark ``(tenant, rule, device)`` as having just fired an alert."""
    key = _key(tenant_id, rule_id, device_id)
    ttl = _window_seconds()
    redis = await get_redis()
    if redis is not None:
        try:
            await redis.set(key, "1", ex=ttl)
            return
        except Exception:
            logger.warning("Redis SET failed for %s; falling back to memory", key)

    _memory[key] = time.time() + ttl


def _reset_memory_for_tests() -> None:
    """Test helper — clear the in-memory fallback between tests."""
    _memory.clear()
