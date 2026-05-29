"""Unit tests for config management service layer — cache + override merging."""

from __future__ import annotations

from app.config_management.service.cache import ConfigCache
from app.config_management.service.overrides import _deep_merge


class TestConfigCache:
    def test_set_and_get(self):
        c = ConfigCache(ttl=60)
        c.set("key1", {"data": True})
        assert c.get("key1") == {"data": True}

    def test_get_missing_returns_none(self):
        c = ConfigCache(ttl=60)
        assert c.get("nonexistent") is None

    def test_invalidate_removes_key(self):
        c = ConfigCache(ttl=60)
        c.set("key1", "value")
        c.invalidate("key1")
        assert c.get("key1") is None

    def test_invalidate_prefix(self):
        c = ConfigCache(ttl=60)
        c.set("profile:dwc", {"a": 1})
        c.set("profile:soil", {"b": 2})
        c.set("templates:all", {"c": 3})
        c.invalidate_prefix("profile:")
        assert c.get("profile:dwc") is None
        assert c.get("profile:soil") is None
        assert c.get("templates:all") == {"c": 3}

    def test_clear_removes_all(self):
        c = ConfigCache(ttl=60)
        c.set("a", 1)
        c.set("b", 2)
        c.clear()
        assert c.get("a") is None
        assert c.get("b") is None

    def test_expired_entry_returns_none(self):
        c = ConfigCache(ttl=0)  # Immediate expiry
        c.set("key", "value")
        # With ttl=0, any get after set will expire
        import time

        time.sleep(0.01)
        assert c.get("key") is None


class TestDeepMerge:
    def test_simple_override(self):
        base = {"temp_min": 65, "temp_max": 80, "humidity": 60}
        override = {"temp_min": 70}
        result = _deep_merge(base, override)
        assert result == {"temp_min": 70, "temp_max": 80, "humidity": 60}

    def test_nested_override(self):
        base = {
            "environment": {"temp_min": 65, "temp_max": 80},
            "nutrients": {"ec_target": 1.2},
        }
        override = {"environment": {"temp_min": 70}}
        result = _deep_merge(base, override)
        assert result["environment"]["temp_min"] == 70
        assert result["environment"]["temp_max"] == 80
        assert result["nutrients"]["ec_target"] == 1.2

    def test_override_adds_new_keys(self):
        base = {"a": 1}
        override = {"b": 2}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 2}

    def test_override_replaces_non_dict_with_dict(self):
        base = {"val": 42}
        override = {"val": {"nested": True}}
        result = _deep_merge(base, override)
        assert result == {"val": {"nested": True}}

    def test_does_not_mutate_originals(self):
        base = {"a": {"b": 1}}
        override = {"a": {"b": 2}}
        result = _deep_merge(base, override)
        assert base["a"]["b"] == 1
        assert result["a"]["b"] == 2

    def test_empty_override_returns_base(self):
        base = {"x": 1, "y": 2}
        result = _deep_merge(base, {})
        assert result == base
