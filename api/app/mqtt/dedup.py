"""MQTT ingest idempotency.

Drops duplicate sensor payloads within a short window so that QoS-1
redelivery (broker reconnect, worker crash-and-retry) and firmware
re-publish-after-no-ack don't cause duplicate rows in
``bucket_sensor_readings`` / ``tent_sensor_readings`` or duplicate
alert firings downstream.

Dedup key
---------
``mqtt:dedup:{tenant_id}:{device_id}:{sensor_type}:{sha256(payload)}``

Hashing the payload bytes (not its parsed form) means two byte-identical
messages within the window are coalesced regardless of key ordering,
whitespace, or numeric formatting. Including ``sensor_type`` keeps
distinct topics from colliding when a device publishes both ``ambient``
and ``readings`` with the same payload.

Window
------
60 seconds by default, overridable via ``MQTT_DEDUP_SECONDS``. That's
deliberately short: most legitimate device publish intervals are
\u2265 30 s, and we'd rather drop a real reading occasionally than
double-count after a broker hiccup. Setting the env var to ``0``
disables dedup entirely (useful for tests).

Storage
-------
Same pattern as ``app.automation.suppression``:

* Redis (preferred) \u2014 ``SET key 1 EX ttl NX`` so the check-and-claim
  is atomic across worker replicas.
* In-process dict (fallback) \u2014 used only when Redis is unavailable
  (typically local dev / tests). Loses state on restart, which is fine
  for those environments and matches the suppression module's behaviour.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time

from app.middleware.redis_store import get_redis

logger = logging.getLogger("tendril.mqtt.dedup")

# In-process fallback: key -> unix expiry timestamp.
_memory: dict[str, float] = {}


def _window_seconds() -> int:
    return int(os.environ.get("MQTT_DEDUP_SECONDS", "60"))


def _key(tenant_id: object, device_id: str, sensor_type: str, payload_bytes: bytes) -> str:
    digest = hashlib.sha256(payload_bytes).hexdigest()[:16]
    return f"mqtt:dedup:{tenant_id}:{device_id}:{sensor_type}:{digest}"


async def claim_message(
    tenant_id: object,
    device_id: str,
    sensor_type: str,
    payload_bytes: bytes,
) -> bool:
    """Attempt to claim ownership of this MQTT message.

    Returns ``True`` if this is the first time we've seen this exact
    payload from this device on this topic within the dedup window
    (caller should proceed with storage). Returns ``False`` if the
    same message was already seen (caller should drop the message
    silently).

    Atomic in Redis via ``SET ... NX EX``. The memory fallback's
    check-then-set is racy in principle but worker replicas all share
    Redis in any deployment that has it, and the fallback exists only
    for local dev / tests where there's a single worker.
    """
    ttl = _window_seconds()
    if ttl <= 0:
        # Dedup disabled via env var.
        return True

    key = _key(tenant_id, device_id, sensor_type, payload_bytes)
    redis = await get_redis()
    if redis is not None:
        try:
            # SET ... NX returns truthy when the key was set, falsy when
            # it already existed. That gives us the atomic check-and-claim.
            claimed = await redis.set(key, "1", ex=ttl, nx=True)
            return bool(claimed)
        except Exception:
            logger.warning("Redis SET NX failed for %s; falling back to memory", key)

    # Memory fallback: evict expired, then check-and-set.
    now = time.time()
    expiry = _memory.get(key)
    if expiry is not None and expiry > now:
        return False
    _memory[key] = now + ttl
    return True


def _reset_memory_for_tests() -> None:
    """Test helper \u2014 clear the in-memory fallback between tests."""
    _memory.clear()
