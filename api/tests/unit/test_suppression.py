"""Tests for alert suppression / dedup window."""

from __future__ import annotations

import pytest
import pytest_asyncio

from app.automation import suppression

pytestmark = pytest.mark.asyncio(loop_scope="session")


# Override the autouse DB-cleaning fixture from conftest — these are
# pure unit tests that don't touch the DB.
@pytest_asyncio.fixture(autouse=True)
async def _clean_tables():
    yield


@pytest.fixture(autouse=True)
def _clear_memory_state():
    suppression._reset_memory_for_tests()
    yield
    suppression._reset_memory_for_tests()


class TestSuppression:
    async def test_first_fire_is_not_suppressed(self):
        assert await suppression.is_suppressed("t1", "rule_a", "dev_1") is False

    async def test_mark_then_check_is_suppressed(self):
        await suppression.mark_fired("t1", "rule_a", "dev_1")
        assert await suppression.is_suppressed("t1", "rule_a", "dev_1") is True

    async def test_different_device_not_suppressed(self):
        await suppression.mark_fired("t1", "rule_a", "dev_1")
        assert await suppression.is_suppressed("t1", "rule_a", "dev_2") is False

    async def test_different_rule_not_suppressed(self):
        await suppression.mark_fired("t1", "rule_a", "dev_1")
        assert await suppression.is_suppressed("t1", "rule_b", "dev_1") is False

    async def test_different_tenant_not_suppressed(self):
        await suppression.mark_fired("t1", "rule_a", "dev_1")
        assert await suppression.is_suppressed("t2", "rule_a", "dev_1") is False

    async def test_window_seconds_from_env(self, monkeypatch):
        monkeypatch.setenv("ALERT_SUPPRESSION_MINUTES", "15")
        assert suppression._window_seconds() == 15 * 60

    async def test_window_seconds_default(self, monkeypatch):
        monkeypatch.delenv("ALERT_SUPPRESSION_MINUTES", raising=False)
        assert suppression._window_seconds() == 30 * 60

    async def test_memory_expiry(self, monkeypatch):
        """When TTL elapses, the in-memory fallback should report not-suppressed."""

        # Force memory fallback by ensuring get_redis returns None.
        async def _no_redis():
            return None

        monkeypatch.setattr(suppression, "get_redis", _no_redis)

        # Set window to effectively 0 by mocking time.time to advance past expiry.
        await suppression.mark_fired("t1", "rule_a", "dev_1")
        # Advance "now" beyond the suppression window.
        import time

        real_time = time.time
        monkeypatch.setattr(suppression.time, "time", lambda: real_time() + 10_000)
        assert await suppression.is_suppressed("t1", "rule_a", "dev_1") is False
