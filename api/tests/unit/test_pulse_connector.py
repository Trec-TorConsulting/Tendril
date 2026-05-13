"""Tests for the Pulse Grow integration connector."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio

from app.integrations.connectors.base import ConnectorResult, get_connector_class
from app.integrations.connectors.pulse import (
    DiscoveredDevice,
    PulseConfig,
    PulseConnector,
)
from app.integrations.models import IntegrationConfig, IntegrationDeviceMap
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_REQUEST = httpx.Request("GET", "https://api.pulsegrow.com/")


def _resp(status_code: int = 200, json: Any = None) -> httpx.Response:
    """Build an httpx.Response with a request set (needed for raise_for_status)."""
    r = httpx.Response(status_code, json=json or {})
    r._request = _FAKE_REQUEST
    return r


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


def _make_config(tenant_id, **overrides) -> IntegrationConfig:
    cfg = IntegrationConfig(
        id=overrides.pop("id", uuid4()),
        tenant_id=tenant_id,
        type="pulse",
        name="Test Pulse",
        config="encrypted-placeholder",
        webhook_secret="test-secret",
        enabled=True,
        poll_interval_s=300,
    )
    return cfg


def _make_device_map(
    tenant_id,
    integration_id,
    external_id: str = "123",
    tent_id=None,
    bucket_id=None,
    sensor_mapping=None,
) -> IntegrationDeviceMap:
    return IntegrationDeviceMap(
        id=uuid4(),
        tenant_id=tenant_id,
        integration_id=integration_id,
        external_id=external_id,
        external_name=f"Device {external_id}",
        tent_id=tent_id or uuid4(),
        bucket_id=bucket_id,
        sensor_mapping=sensor_mapping or {},
        enabled=True,
    )


def _make_pulse_device_dto(
    device_id: int = 123,
    temp: float = 78.5,
    humidity: float = 55.0,
    vpd: float = 1.2,
    co2: int = 800,
    lux: float = 45000.0,
    dew_point_f: float = 60.1,
    par: float = 650.0,
    air_pressure: float = 29.92,
    voc: int = 150,
) -> dict[str, Any]:
    return {
        "deviceId": device_id,
        "deviceType": 1,
        "pluggedIn": True,
        "batteryV": 4.1,
        "signalStrength": -45,
        "createdAt": "2026-04-28T12:00:00Z",
        "temperatureF": temp,
        "humidityRh": humidity,
        "vpd": vpd,
        "co2": co2,
        "lightLux": lux,
        "dpF": dew_point_f,
        "par": par,
        "airPressure": air_pressure,
        "voc": voc,
        "name": f"Pulse Device {device_id}",
    }


def _make_all_devices_response(device_dtos: list[dict] | None = None) -> dict:
    return {
        "deviceViewDtos": device_dtos or [_make_pulse_device_dto()],
        "universalSensorViews": [],
        "hubViewDtos": [],
        "controlsViewDtos": [],
    }


def _make_hub_sensor_response(
    soil_moisture: float = 42.5,
    soil_temp: float = 72.0,
) -> dict:
    return {
        "sensorType": 1,
        "deviceType": 3,
        "name": "VWC Probe 1",
        "dataPointDto": {
            "dataPointValues": [
                {"name": "soil_moisture", "value": soil_moisture},
                {"name": "soil_temp", "value": soil_temp},
            ],
            "sensorId": 456,
            "createdAt": "2026-04-28T12:00:00Z",
        },
    }


# ---------------------------------------------------------------------------
# Config Validation
# ---------------------------------------------------------------------------


class TestPulseConfig:
    def test_valid_config(self):
        cfg = PulseConfig(api_key="abcdefghij-test-key")
        assert cfg.api_key == "abcdefghij-test-key"
        assert cfg.base_url == "https://api.pulsegrow.com"

    def test_custom_base_url(self):
        cfg = PulseConfig(api_key="abcdefghij-test-key", base_url="https://custom.api.com")
        assert cfg.base_url == "https://custom.api.com"

    def test_missing_api_key(self):
        with pytest.raises(ValueError):
            PulseConfig()

    def test_api_key_too_short(self):
        with pytest.raises(ValueError):
            PulseConfig(api_key="short")


# ---------------------------------------------------------------------------
# Connector Registration
# ---------------------------------------------------------------------------


class TestConnectorRegistration:
    def test_pulse_registered(self):
        cls = get_connector_class("pulse")
        assert cls is PulseConnector

    def test_integration_type(self):
        assert PulseConnector.integration_type == "pulse"


# ---------------------------------------------------------------------------
# Poll — Device Readings (Tent)
# ---------------------------------------------------------------------------


class TestPollDevices:
    async def test_poll_success_single_device(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        tent_id = uuid4()
        dm = _make_device_map(tenant_id, cfg.id, external_id="123", tent_id=tent_id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm],
        )

        mock_response = _resp(200, _make_all_devices_response())

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await connector.poll()

        assert result.status == "success"
        assert result.readings_count == 1
        reading = result.readings[0]
        assert reading["target"] == "tent"
        assert reading["external_id"] == "123"
        assert reading["tent_id"] == str(tent_id)
        assert reading["ambient_temp_f"] == 78.5
        assert reading["ambient_humidity"] == 55.0
        assert reading["vpd"] == 1.2
        assert reading["co2"] == 800.0
        assert reading["lux"] == 45000.0
        assert reading["dew_point_f"] == 60.1
        assert reading["par_ppfd"] == 650.0
        assert reading["air_pressure"] == 29.92
        assert reading["voc"] == 150.0

    async def test_poll_multiple_devices(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        dm1 = _make_device_map(tenant_id, cfg.id, external_id="100")
        dm2 = _make_device_map(tenant_id, cfg.id, external_id="200")

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm1, dm2],
        )

        response_data = _make_all_devices_response(
            [
                _make_pulse_device_dto(device_id=100, temp=75.0),
                _make_pulse_device_dto(device_id=200, temp=80.0),
                _make_pulse_device_dto(device_id=999, temp=60.0),  # unmapped
            ]
        )
        mock_response = _resp(200, response_data)

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await connector.poll()

        assert result.status == "success"
        assert result.readings_count == 2
        temps = {r["external_id"]: r["ambient_temp_f"] for r in result.readings}
        assert temps["100"] == 75.0
        assert temps["200"] == 80.0

    async def test_poll_no_mapped_devices(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[],
        )

        result = await connector.poll()
        assert result.status == "success"
        assert result.readings_count == 0

    async def test_poll_device_missing_fields(self):
        """Devices with NULL fields should still produce partial readings."""
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        dm = _make_device_map(tenant_id, cfg.id, external_id="123")

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm],
        )

        # Device DTO with only temp and humidity (e.g., Pulse One without CO2)
        minimal_dto = {
            "deviceId": 123,
            "deviceType": 1,
            "temperatureF": 72.0,
            "humidityRh": 50.0,
        }
        mock_response = _resp(200, _make_all_devices_response([minimal_dto]))

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            result = await connector.poll()

        assert result.status == "success"
        assert result.readings_count == 1
        reading = result.readings[0]
        assert reading["ambient_temp_f"] == 72.0
        assert reading["ambient_humidity"] == 50.0
        assert "co2" not in reading  # NULL fields omitted


# ---------------------------------------------------------------------------
# Poll — Hub Sensors (Bucket)
# ---------------------------------------------------------------------------


class TestPollHubSensors:
    async def test_poll_hub_sensor_success(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        bucket_id = uuid4()
        dm = _make_device_map(
            tenant_id,
            cfg.id,
            external_id="456",
            tent_id=None,
            bucket_id=bucket_id,
            sensor_mapping={"soil_moisture": "soil_moisture", "soil_temp": "soil_temp"},
        )

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm],
        )

        async def mock_get(url, **kwargs):
            if "/all-devices" in url:
                return _resp(200, _make_all_devices_response([]))
            if "/sensors/" in url:
                return _resp(200, _make_hub_sensor_response())
            return _resp(404)

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, side_effect=mock_get):
            result = await connector.poll()

        assert result.status == "success"
        assert result.readings_count == 1
        reading = result.readings[0]
        assert reading["target"] == "bucket"
        assert reading["bucket_id"] == str(bucket_id)
        assert reading["soil_moisture"] == 42.5
        assert reading["soil_temp"] == 72.0

    async def test_poll_hub_sensor_api_error(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        dm = _make_device_map(
            tenant_id,
            cfg.id,
            external_id="456",
            tent_id=None,
            bucket_id=uuid4(),
        )

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm],
        )

        async def mock_get(url, **kwargs):
            if "/all-devices" in url:
                return _resp(200, _make_all_devices_response([]))
            raise httpx.RequestError("Connection refused")

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, side_effect=mock_get):
            result = await connector.poll()

        assert result.status == "error"
        assert any("Network error" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    async def test_poll_auth_failure_401(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        dm = _make_device_map(tenant_id, cfg.id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "bad-key-12345678"},
            device_maps=[dm],
        )

        mock_response = _resp(401)

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError("Unauthorized", request=_FAKE_REQUEST, response=mock_response)
            result = await connector.poll()

        assert result.status == "error"
        assert any("authentication failed" in e for e in result.errors)

    async def test_poll_rate_limit_429(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        dm = _make_device_map(tenant_id, cfg.id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm],
        )

        mock_response = _resp(429)

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError("Rate Limited", request=_FAKE_REQUEST, response=mock_response)
            result = await connector.poll()

        assert result.status == "error"
        assert any("rate limit" in e for e in result.errors)

    async def test_poll_server_error_500(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        dm = _make_device_map(tenant_id, cfg.id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm],
        )

        mock_response = _resp(500)

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError("Server Error", request=_FAKE_REQUEST, response=mock_response)
            result = await connector.poll()

        assert result.status == "error"
        assert any("HTTP 500" in e for e in result.errors)

    async def test_poll_network_timeout(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)
        dm = _make_device_map(tenant_id, cfg.id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[dm],
        )

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection timed out")
            result = await connector.poll()

        assert result.status == "error"
        assert any("Network error" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Webhook (not supported)
# ---------------------------------------------------------------------------


class TestWebhook:
    async def test_webhook_returns_error(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[],
        )

        result = await connector.handle_webhook({"some": "data"})
        assert result.status == "error"
        assert any("not support webhooks" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class TestDiscovery:
    async def test_discover_devices_success(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345678"},
            device_maps=[],
        )

        all_devices_data = {
            "deviceViewDtos": [
                {**_make_pulse_device_dto(device_id=100), "name": "Tent A Monitor"},
                {**_make_pulse_device_dto(device_id=200), "deviceType": 2, "name": "Pro Monitor"},
            ],
            "universalSensorViews": [],
            "hubViewDtos": [
                {"id": 10, "name": "Hub Alpha"},
            ],
            "controlsViewDtos": [],
        }

        async def mock_get(url, **kwargs):
            if "/all-devices" in url:
                return _resp(200, all_devices_data)
            if "/sensors/ids" in url:
                return _resp(200, [456, 789])
            if "/sensors/456/details" in url:
                return _resp(200, [{"name": "VWC Probe 1"}])
            if "/sensors/789/details" in url:
                return _resp(200, [{"name": "pH Probe"}])
            return _resp(404)

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, side_effect=mock_get):
            devices = await connector.discover_devices()

        assert len(devices) == 5  # 2 devices + 1 hub + 2 sensors
        types = {d.device_type for d in devices}
        assert "pulse_one" in types
        assert "pulse_pro" in types
        assert "hub" in types
        assert "hub_sensor" in types

        # Check device has latest reading preview
        tent_a = next(d for d in devices if d.name == "Tent A Monitor")
        assert tent_a.latest_reading is not None
        assert "ambient_temp_f" in tent_a.latest_reading

    async def test_discover_auth_failure(self):
        tenant_id = uuid4()
        cfg = _make_config(tenant_id)

        connector = PulseConnector(
            config=cfg,
            decrypted_config={"api_key": "bad-key-12345678"},
            device_maps=[],
        )

        mock_response = _resp(401)

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError("Unauthorized", request=_FAKE_REQUEST, response=mock_response)
            with pytest.raises(httpx.HTTPStatusError):
                await connector.discover_devices()


# ---------------------------------------------------------------------------
# ConnectorResult
# ---------------------------------------------------------------------------


class TestConnectorResult:
    def test_success_status(self):
        r = ConnectorResult()
        r.readings.append({"some": "data"})
        assert r.status == "success"
        assert r.readings_count == 1
        assert r.error_message is None

    def test_error_status(self):
        r = ConnectorResult()
        r.errors.append("Something failed")
        assert r.status == "error"
        assert r.readings_count == 0
        assert r.error_message == "Something failed"

    def test_partial_status(self):
        r = ConnectorResult()
        r.readings.append({"some": "data"})
        r.errors.append("One device failed")
        assert r.status == "partial"
        assert r.readings_count == 1
        assert "One device failed" in r.error_message


# ---------------------------------------------------------------------------
# API Integration Tests (HTTP routes)
# ---------------------------------------------------------------------------


class TestPulseIntegrationAPI:
    async def test_create_pulse_integration(self, client, tenant):
        resp = await client.post(
            "/v1/integrations",
            json={
                "type": "pulse",
                "name": "My Pulse Monitor",
                "config": {"api_key": "test-api-key-1234567890"},
                "poll_interval_s": 300,
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "pulse"
        assert data["poll_interval_s"] == 300
        # API key should be redacted
        assert "••••" in data["config"]["api_key"]

    async def test_trigger_manual_sync(self, client, tenant):
        # Create integration
        create_resp = await client.post(
            "/v1/integrations",
            json={
                "type": "pulse",
                "name": "My Pulse",
                "config": {"api_key": "test-api-key-1234567890"},
                "poll_interval_s": 300,
            },
            headers=tenant["headers"],
        )
        integration_id = create_resp.json()["id"]

        # Mock the connector's poll method
        mock_result = ConnectorResult()
        mock_result.readings.append({"target": "tent", "ambient_temp_f": 75.0})

        with patch.object(PulseConnector, "poll", new_callable=AsyncMock, return_value=mock_result):
            resp = await client.post(
                f"/v1/integrations/{integration_id}/sync",
                headers=tenant["headers"],
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["readings_count"] == 1

    async def test_discover_devices_endpoint(self, client, tenant):
        # Create integration
        create_resp = await client.post(
            "/v1/integrations",
            json={
                "type": "pulse",
                "name": "My Pulse",
                "config": {"api_key": "test-api-key-1234567890"},
            },
            headers=tenant["headers"],
        )
        integration_id = create_resp.json()["id"]

        mock_devices = [
            DiscoveredDevice(
                external_id="123",
                name="Tent A Monitor",
                device_type="pulse_one",
                latest_reading={"ambient_temp_f": 78.5},
            ),
        ]

        with patch.object(PulseConnector, "discover_devices", new_callable=AsyncMock, return_value=mock_devices):
            resp = await client.post(
                f"/v1/integrations/{integration_id}/discover",
                headers=tenant["headers"],
            )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["external_id"] == "123"
        assert data[0]["name"] == "Tent A Monitor"
        assert data[0]["device_type"] == "pulse_one"
        assert data[0]["latest_reading"]["ambient_temp_f"] == 78.5

    async def test_discover_unimplemented_connector(self, client, tenant):
        # Create integration with an unknown type
        create_resp = await client.post(
            "/v1/integrations",
            json={
                "type": "unknown_type",
                "name": "Unknown",
                "config": {},
            },
            headers=tenant["headers"],
        )
        integration_id = create_resp.json()["id"]

        resp = await client.post(
            f"/v1/integrations/{integration_id}/discover",
            headers=tenant["headers"],
        )
        assert resp.status_code == 501
