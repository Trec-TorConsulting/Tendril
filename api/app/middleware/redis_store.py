"""Shared Redis connection for middleware (rate limiting, brute-force).

Falls back to in-memory dicts when Redis is unavailable so local dev
and single-instance deployments work without any extra infrastructure.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("tendril.middleware.redis")

_redis = None
_fallback = False


async def _get_redis():
    """Return a redis.asyncio client, or *None* if unavailable."""
    global _redis, _fallback

    if _fallback:
        return None
    if _redis is not None:
        return _redis

    redis_url = os.environ.get("REDIS_URL", "")
    if not redis_url:
        # Also check Settings if available
        try:
            from app.config import get_settings

            redis_url = get_settings().redis_url
        except Exception:
            logger.debug("Could not read REDIS_URL from settings; falling back to env", exc_info=True)
    if not redis_url:
        logger.info("REDIS_URL not set — middleware will use in-memory state")
        _fallback = True
        return None

    try:
        from redis.asyncio import from_url

        _redis = from_url(redis_url, decode_responses=True)
        await _redis.ping()
        logger.info("Redis connected for middleware state")
        return _redis
    except Exception:
        logger.warning("Redis unavailable — falling back to in-memory state")
        _fallback = True
        return None


async def get_redis():
    """Public accessor — always safe to call."""
    return await _get_redis()
