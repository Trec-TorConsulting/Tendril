"""Unit tests for Tuya connector value mapping."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.integrations.connectors.tuya import TuyaConnector


def _make_connector() -> TuyaConnector:
    config = MagicMock()
    config.tenant_id = uuid.uuid4()
    config.id = uuid.uuid4()

    decrypted = {
        "access_id": "test-access-id",
        "access_secret": "test-access-secret",
        "region": "us",
    }

    dm = MagicMock()
    dm.external_id = "tuya-device-1"
    dm.enabled = True
    dm.sensor_mapping = {}
    dm.bucket_id = uuid.uuid4()
    dm.tent_id = None

    return TuyaConnector(config, decrypted, [dm])


def _device_map(connector: TuyaConnector):
    return connector.device_maps[0]


def test_map_statuses_ph_uses_shadow_scale_metadata():
    connector = _make_connector()
    dm = _device_map(connector)

    statuses = [{"code": "ph", "value": 53, "scale": 1}]
    reading = connector._map_statuses(statuses, dm)

    assert reading["ph"] == 5.3


def test_map_statuses_ph_falls_back_to_legacy_heuristic_without_scale():
    connector = _make_connector()
    dm = _device_map(connector)

    statuses = [{"code": "ph", "value": 575}]
    reading = connector._map_statuses(statuses, dm)

    assert reading["ph"] == 5.75


def test_map_statuses_ec_uses_shadow_scale_metadata():
    connector = _make_connector()
    dm = _device_map(connector)

    statuses = [{"code": "ec", "value": 614, "scale": 2}]
    reading = connector._map_statuses(statuses, dm)

    assert reading["ec"] == 6.14


def test_map_statuses_water_temp_uses_shadow_scale_metadata():
    connector = _make_connector()
    dm = _device_map(connector)

    statuses = [{"code": "water_temp", "value": 196, "scale": 1}]
    reading = connector._map_statuses(statuses, dm)

    assert reading["water_temp_c"] == 19.6


@pytest.mark.asyncio(loop_scope="session")
async def test_debug_latest_prefers_shadow_when_available(monkeypatch):
    connector = _make_connector()
    dm = _device_map(connector)

    async def _fake_shadow(client, device_id):
        assert device_id == dm.external_id
        return [{"code": "ph", "value": 53, "scale": 1}]

    async def _fake_api_get(client, path):
        assert path.endswith("/status")
        return {"success": True, "result": [{"code": "ph", "value": 600}]}

    monkeypatch.setattr(connector, "_fetch_shadow_properties", _fake_shadow)
    monkeypatch.setattr(connector, "_api_get", _fake_api_get)

    out = await connector.debug_latest(dm.external_id, dm)

    assert out["mapped_source"] == "shadow"
    assert out["mapped_reading"]["ph"] == 5.3
    assert out["status_error"] is None


@pytest.mark.asyncio(loop_scope="session")
async def test_debug_latest_falls_back_to_status_when_shadow_empty(monkeypatch):
    connector = _make_connector()
    dm = _device_map(connector)

    async def _fake_shadow(client, device_id):
        return []

    async def _fake_api_get(client, path):
        return {"success": True, "result": [{"code": "ph", "value": 540}]}

    monkeypatch.setattr(connector, "_fetch_shadow_properties", _fake_shadow)
    monkeypatch.setattr(connector, "_api_get", _fake_api_get)

    out = await connector.debug_latest(dm.external_id, dm)

    assert out["mapped_source"] == "status"
    assert out["mapped_reading"]["ph"] == 5.4
