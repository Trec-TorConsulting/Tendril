"""In-process TTL cache for config service — avoids repeated DB reads for rarely-changing data."""

from __future__ import annotations

import time
from typing import Any

_DEFAULT_TTL = 300  # 5 minutes


class ConfigCache:
    """Simple in-process cache with TTL expiration and manual invalidation."""

    def __init__(self, ttl: int = _DEFAULT_TTL):
        self._ttl = ttl
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        ts, value = entry
        if time.monotonic() - ts > self._ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.monotonic(), value)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        keys_to_remove = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._store[k]

    def clear(self) -> None:
        self._store.clear()


# Module-level singleton
cache = ConfigCache()
