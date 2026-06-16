"""Tests for MQTT ingest idempotency / dedup window."""

from __future__ import annotations

import pytest
import pytest_asyncio

from app.mqtt import dedup

pytestmark = pytest.mark.asyncio(loop_scope="session")


# Pure unit tests — no DB needed.
@pytest_asyncio.fixture(autouse=True)
async def _clean_tables():
    yield


@pytest.fixture(autouse=True)
def _clear_memory_state():
    dedup._reset_memory_for_tests()
    yield
    dedup._reset_memory_for_tests()


# Force the memory fallback for these tests so the Redis path doesn't
# leak between local runs / shared CI infrastructure.
@pytest.fixture(autouse=True)
def _disable_redis(monkeypatch):
    async def _no_redis():
        return None

    monkeypatch.setattr(dedup, "get_redis", _no_redis)


PAYLOAD_A = b'{"ph":6.1,"ec":1.8,"position":1}'
PAYLOAD_B = b'{"ph":6.2,"ec":1.8,"position":1}'


class TestClaimMessage:
    async def test_first_claim_succeeds(self):
        assert await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A) is True

    async def test_duplicate_within_window_is_rejected(self):
        await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A)
        assert await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A) is False

    async def test_different_payload_same_device_passes(self):
        await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A)
        assert await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_B) is True

    async def test_same_payload_different_device_passes(self):
        await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A)
        assert await dedup.claim_message("t1", "dev_2", "readings", PAYLOAD_A) is True

    async def test_same_payload_different_tenant_passes(self):
        await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A)
        assert await dedup.claim_message("t2", "dev_1", "readings", PAYLOAD_A) is True

    async def test_same_payload_different_sensor_type_passes(self):
        """A device may publish the same JSON shape on both /sensor/readings and
        /sensor/ambient (e.g. constant zero values during a reset). Both must
        be accepted."""
        await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A)
        assert await dedup.claim_message("t1", "dev_1", "ambient", PAYLOAD_A) is True

    async def test_window_zero_disables_dedup(self, monkeypatch):
        monkeypatch.setenv("MQTT_DEDUP_SECONDS", "0")
        await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A)
        # With dedup disabled, even an identical payload claims successfully.
        assert await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A) is True

    async def test_window_default_is_60s(self, monkeypatch):
        monkeypatch.delenv("MQTT_DEDUP_SECONDS", raising=False)
        assert dedup._window_seconds() == 60

    async def test_window_overridable_via_env(self, monkeypatch):
        monkeypatch.setenv("MQTT_DEDUP_SECONDS", "300")
        assert dedup._window_seconds() == 300

    async def test_memory_expiry(self, monkeypatch):
        """Once TTL elapses, the same payload claims successfully again."""
        await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A)
        assert await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A) is False

        # Fast-forward "now" past the dedup window.
        import time

        real_time = time.time
        monkeypatch.setattr(dedup.time, "time", lambda: real_time() + 10_000)
        assert await dedup.claim_message("t1", "dev_1", "readings", PAYLOAD_A) is True
