"""Tests for the Ecowitt integration connector (dual-mode: webhook + cloud)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
import pytest
from app.integrations.connectors.base import ConnectorResult, get_connector_class
from app.integrations.connectors.ecowitt import (
    DiscoveredDevice,
    EcowittConfig,
    EcowittConnector,
    _extract_value,
    _f_to_c,
    _in_to_mm,
    _inhg_to_hpa,
    _mph_to_kmh,
    write_ecowitt_readings,
)
from app.integrations.models import IntegrationConfig, IntegrationDeviceMap

pytestmark = pytest.mark.asyncio(loop_scope="session")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_REQUEST = httpx.Request("GET", "https://api.ecowitt.net/api/v3/device/real_time")


def _resp(status_code: int = 200, json: Any = None) -> httpx.Response:
    r = httpx.Response(status_code, json=json or {})
    r._request = _FAKE_REQUEST
    return r


# Sample Ecowitt cloud API response
_CLOUD_RESPONSE = {
    "code": 0,
    "msg": "success",
    "time": "1745971200",
    "data": {
        "outdoor": {
            "temperature": {"time": "1745971200", "unit": "℃", "value": "22.5"},
            "humidity": {"time": "1745971200", "unit": "%", "value": "65"},
            "dew_point": {"time": "1745971200", "unit": "℃", "value": "15.3"},
        },
        "wind": {
            "wind_speed": {"time": "1745971200", "unit": "km/h", "value": "12.5"},
        },
        "rainfall": {
            "daily": {"time": "1745971200", "unit": "mm", "value": "3.2"},
        },
        "solar_and_uvi": {
            "uvi": {"time": "1745971200", "unit": "", "value": "6"},
        },
        "pressure": {
            "relative": {"time": "1745971200", "unit": "hPa", "value": "1013.2"},
        },
        "soil_ch1": {
            "soilmoisture": {"time": "1745971200", "unit": "%", "value": "42"},
        },
        "soil_ch2": {
            "soilmoisture": {"time": "1745971200", "unit": "%", "value": "38"},
        },
        "ch_soil_ec_temp_hum1": {
            "soilmoisture": {"time": "1745971200", "unit": "%", "value": "55"},
            "temperature": {"time": "1745971200", "unit": "℃", "value": "18.5"},
            "ec": {"time": "1745971200", "unit": "μS/cm", "value": "450"},
        },
        "temp_and_humidity_ch1": {
            "temperature": {"time": "1745971200", "unit": "℃", "value": "24.0"},
            "humidity": {"time": "1745971200", "unit": "%", "value": "70"},
        },
        "leaf_ch1": {
            "leaf_wetness": {"time": "1745971200", "unit": "%", "value": "73"},
        },
    },
}

# Sample webhook payload (imperial units, form-encoded style)
_WEBHOOK_PAYLOAD = {
    "PASSKEY": "aabbccddeeff",
    "stationtype": "GW2000A_V2.3.2",
    "dateutc": "2026-04-28+22:30:00",
    "tempf": "72.5",
    "humidity": "65",
    "dewptf": "59.5",
    "windspeedmph": "7.8",
    "dailyrainin": "0.13",
    "uv": "6",
    "baromrelin": "29.92",
    "soilmoisture1": "42",
    "soilmoisture2": "38",
    "temp1f": "75.2",
    "humidity1": "70",
    "leafwetness_ch1": "73",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(tenant_id, **overrides) -> IntegrationConfig:
    return IntegrationConfig(
        id=overrides.pop("id", uuid4()),
        tenant_id=tenant_id,
        type="ecowitt",
        name="Test Ecowitt",
        config="encrypted-placeholder",
        webhook_secret="test-secret",
        enabled=True,
        poll_interval_s=300,
    )


def _make_device_map(
    tenant_id,
    integration_id,
    external_id: str = "weather",
    tent_id=None,
    bucket_id=None,
) -> IntegrationDeviceMap:
    return IntegrationDeviceMap(
        id=uuid4(),
        tenant_id=tenant_id,
        integration_id=integration_id,
        external_id=external_id,
        external_name=f"Device {external_id}",
        tent_id=tent_id or uuid4(),
        bucket_id=bucket_id,
        sensor_mapping={},
        enabled=True,
    )


def _make_full_maps(tenant_id, integration_id, tent_id=None, bucket_id=None):
    """Create device maps for weather station, soil channels, and temp/hum channels."""
    tid = tent_id or uuid4()
    bid = bucket_id or uuid4()
    bid2 = uuid4()
    bid_leaf = uuid4()
    return [
        _make_device_map(tenant_id, integration_id, "weather", tent_id=tid),
        _make_device_map(tenant_id, integration_id, "soil_ch1", tent_id=tid, bucket_id=bid),
        _make_device_map(tenant_id, integration_id, "soil_ch2", tent_id=tid, bucket_id=bid2),
        _make_device_map(tenant_id, integration_id, "ch_soil_ec_temp_hum1", tent_id=tid, bucket_id=bid),
        _make_device_map(tenant_id, integration_id, "temp_and_humidity_ch1", tent_id=tid),
        _make_device_map(tenant_id, integration_id, "leaf_ch1", tent_id=tid, bucket_id=bid_leaf),
    ]


def _make_connector(tenant_id, mode="cloud", device_maps=None):
    cfg = _make_config(tenant_id)
    dc = {
        "mode": mode,
        "application_key": "test-app-key",
        "api_key": "test-api-key",
        "mac": "AA:BB:CC:DD:EE:FF",
    }
    dm = device_maps if device_maps is not None else _make_full_maps(tenant_id, cfg.id)
    return EcowittConnector(config=cfg, decrypted_config=dc, device_maps=dm)


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


class TestEcowittConfig:
    def test_webhook_mode_defaults(self):
        cfg = EcowittConfig()
        assert cfg.mode == "webhook"

    def test_cloud_mode(self):
        cfg = EcowittConfig(
            mode="cloud",
            application_key="app123",
            api_key="key456",
            mac="AA:BB:CC:DD:EE:FF",
        )
        assert cfg.mode == "cloud"
        assert cfg.mac == "AA:BB:CC:DD:EE:FF"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_connector_registered(self):
        cls = get_connector_class("ecowitt")
        assert cls is EcowittConnector


# ---------------------------------------------------------------------------
# Unit conversion helpers
# ---------------------------------------------------------------------------


class TestConversions:
    def test_f_to_c(self):
        assert _f_to_c(32.0) == 0.0
        assert _f_to_c(212.0) == 100.0
        assert _f_to_c(None) is None

    def test_inhg_to_hpa(self):
        hpa = _inhg_to_hpa(29.92)
        assert hpa is not None
        assert abs(hpa - 1013.25) < 0.5
        assert _inhg_to_hpa(None) is None

    def test_mph_to_kmh(self):
        kmh = _mph_to_kmh(10.0)
        assert kmh is not None
        assert abs(kmh - 16.09) < 0.1
        assert _mph_to_kmh(None) is None

    def test_in_to_mm(self):
        mm = _in_to_mm(1.0)
        assert mm is not None
        assert abs(mm - 25.4) < 0.1
        assert _in_to_mm(None) is None

    def test_extract_value(self):
        assert _extract_value({"value": "42.5"}) == 42.5
        assert _extract_value({"value": "abc"}) is None
        assert _extract_value(None) is None
        assert _extract_value({}) is None


# ---------------------------------------------------------------------------
# Cloud API Polling
# ---------------------------------------------------------------------------


class TestCloudPoll:
    async def test_poll_success_all_channels(self):
        connector = _make_connector(uuid4(), mode="cloud")

        async def mock_get(url, **kwargs):
            return _resp(200, _CLOUD_RESPONSE)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "success"
        # Should have: 1 weather + 2 soil_ch + 1 ec_temp + 1 temp_hum + 1 leaf = 6
        assert result.readings_count == 6

        # Verify weather reading
        weather = [r for r in result.readings if r.get("target") == "weather"]
        assert len(weather) == 1
        w = weather[0]
        assert w["temperature_c"] == 22.5
        assert w["humidity_pct"] == 65.0
        assert w["wind_speed_kmh"] == 12.5
        assert w["precipitation_mm"] == 3.2
        assert w["uv_index"] == 6.0
        assert w["pressure_hpa"] == 1013.2
        assert w["dew_point_c"] == 15.3

        # Verify soil readings
        soil = [r for r in result.readings if r.get("target") == "bucket" and "soil_ch" in r.get("external_id", "")]
        assert len(soil) == 2
        assert soil[0]["soil_moisture"] == 42.0

        # Verify EC+temp soil reading
        ec_soil = [r for r in result.readings if r.get("external_id", "").startswith("ch_soil_ec")]
        assert len(ec_soil) == 1
        assert ec_soil[0]["soil_moisture"] == 55.0
        assert ec_soil[0]["soil_temp"] == 18.5
        assert ec_soil[0]["ec"] == 450.0

        # Verify tent sensor reading
        tent = [r for r in result.readings if r.get("target") == "tent"]
        assert len(tent) == 1
        assert tent[0]["ambient_humidity"] == 70.0

    async def test_poll_webhook_mode_noop(self):
        connector = _make_connector(uuid4(), mode="webhook")
        connector.decrypted_config["mode"] = "webhook"
        result = await connector.poll()
        assert result.status == "success"
        assert result.readings_count == 0

    async def test_poll_missing_credentials(self):
        tid = uuid4()
        cfg = _make_config(tid)
        dc = {"mode": "cloud", "application_key": "x", "api_key": None, "mac": None}
        dm = _make_full_maps(tid, cfg.id)
        connector = EcowittConnector(config=cfg, decrypted_config=dc, device_maps=dm)

        result = await connector.poll()
        assert result.status == "error"
        assert "requires application_key" in result.errors[0]

    async def test_poll_api_error_code(self):
        connector = _make_connector(uuid4(), mode="cloud")

        async def mock_get(url, **kwargs):
            return _resp(200, {"code": 40010, "msg": "Invalid application Key", "data": []})

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "error"
        assert "40010" in result.errors[0]

    async def test_poll_http_401(self):
        connector = _make_connector(uuid4(), mode="cloud")

        async def mock_get(url, **kwargs):
            return _resp(401)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "error"
        assert "authentication failed" in result.errors[0]

    async def test_poll_http_429(self):
        connector = _make_connector(uuid4(), mode="cloud")

        async def mock_get(url, **kwargs):
            return _resp(429)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "error"
        assert "rate limit" in result.errors[0]

    async def test_poll_network_error(self):
        connector = _make_connector(uuid4(), mode="cloud")

        async def mock_get(url, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "error"
        assert "Network error" in result.errors[0]


# ---------------------------------------------------------------------------
# Webhook Handling
# ---------------------------------------------------------------------------


class TestWebhook:
    async def test_webhook_full_payload(self):
        connector = _make_connector(uuid4(), mode="webhook")

        result = await connector.handle_webhook(_WEBHOOK_PAYLOAD)

        assert result.status == "success"
        # weather + 2 soil + 1 temp_hum + 1 leaf = 5
        assert result.readings_count == 5

        # Weather reading (imperial → metric)
        weather = [r for r in result.readings if r.get("target") == "weather"]
        assert len(weather) == 1
        w = weather[0]
        assert w["temperature_c"] is not None
        assert abs(w["temperature_c"] - 22.5) < 0.1  # 72.5°F → 22.5°C
        assert w["humidity_pct"] == 65.0
        assert w["precipitation_mm"] is not None
        assert abs(w["precipitation_mm"] - 3.3) < 0.1  # 0.13in → 3.302mm
        assert w["pressure_hpa"] is not None
        assert abs(w["pressure_hpa"] - 1013.2) < 0.2  # 29.92inHg → 1013.2hPa

        # Soil readings
        soil = [r for r in result.readings if r.get("target") == "bucket" and "soil_ch" in r.get("external_id", "")]
        assert len(soil) == 2
        assert soil[0]["soil_moisture"] == 42.0
        assert soil[1]["soil_moisture"] == 38.0

        # Temp/humidity tent reading
        tent = [r for r in result.readings if r.get("target") == "tent"]
        assert len(tent) == 1
        assert tent[0]["ambient_temp_f"] == 75.2

    async def test_webhook_minimal_payload(self):
        """Only weather station data, no soil or temp channels."""
        tid = uuid4()
        cfg = _make_config(tid)
        dm = [_make_device_map(tid, cfg.id, "weather")]
        dc = {"mode": "webhook"}
        connector = EcowittConnector(config=cfg, decrypted_config=dc, device_maps=dm)

        result = await connector.handle_webhook({"tempf": "68.0", "humidity": "50"})

        assert result.status == "success"
        assert result.readings_count == 1
        w = result.readings[0]
        assert abs(w["temperature_c"] - 20.0) < 0.1

    async def test_webhook_no_maps(self):
        """Webhook with no device maps returns no readings."""
        cfg = _make_config(uuid4())
        dc = {"mode": "webhook"}
        connector = EcowittConnector(config=cfg, decrypted_config=dc, device_maps=[])

        result = await connector.handle_webhook(_WEBHOOK_PAYLOAD)

        assert result.status == "success"
        assert result.readings_count == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class TestDiscovery:
    async def test_discover_webhook_mode(self):
        connector = _make_connector(uuid4(), mode="webhook")
        connector.decrypted_config["mode"] = "webhook"

        devices = await connector.discover_devices()
        assert len(devices) >= 1
        ext_ids = [d.external_id for d in devices]
        assert "weather" in ext_ids
        assert "soil_ch1" in ext_ids

    async def test_discover_cloud_mode(self):
        connector = _make_connector(uuid4(), mode="cloud")

        async def mock_get(url, **kwargs):
            return _resp(200, _CLOUD_RESPONSE)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            devices = await connector.discover_devices()

        ext_ids = [d.external_id for d in devices]
        assert "weather" in ext_ids
        assert "soil_ch1" in ext_ids
        assert "soil_ch2" in ext_ids
        assert "ch_soil_ec_temp_hum1" in ext_ids
        assert "temp_and_humidity_ch1" in ext_ids
        assert "leaf_ch1" in ext_ids

    async def test_discover_cloud_api_failure(self):
        connector = _make_connector(uuid4(), mode="cloud")

        async def mock_get(url, **kwargs):
            raise httpx.ConnectTimeout("timeout")

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            devices = await connector.discover_devices()

        assert devices == []


# ---------------------------------------------------------------------------
# Weather-only (no soil maps)
# ---------------------------------------------------------------------------


class TestWeatherOnly:
    async def test_cloud_weather_only(self):
        """Poll with only a weather station map — no soil/temp channels."""
        tid = uuid4()
        cfg = _make_config(tid)
        dm = [_make_device_map(tid, cfg.id, "weather")]
        dc = {
            "mode": "cloud",
            "application_key": "app",
            "api_key": "key",
            "mac": "AA:BB:CC:DD:EE:FF",
        }
        connector = EcowittConnector(config=cfg, decrypted_config=dc, device_maps=dm)

        async def mock_get(url, **kwargs):
            return _resp(200, _CLOUD_RESPONSE)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "success"
        assert result.readings_count == 1
        assert result.readings[0]["target"] == "weather"


# ---------------------------------------------------------------------------
# Partial data (missing sensors in response)
# ---------------------------------------------------------------------------


class TestPartialData:
    async def test_missing_soil_channel_in_response(self):
        """Device maps reference soil_ch3 but it's not in the API response."""
        tid = uuid4()
        cfg = _make_config(tid)
        dm = [
            _make_device_map(tid, cfg.id, "weather"),
            _make_device_map(tid, cfg.id, "soil_ch3", bucket_id=uuid4()),
        ]
        dc = {
            "mode": "cloud",
            "application_key": "app",
            "api_key": "key",
            "mac": "AA:BB:CC:DD:EE:FF",
        }
        connector = EcowittConnector(config=cfg, decrypted_config=dc, device_maps=dm)

        async def mock_get(url, **kwargs):
            return _resp(200, _CLOUD_RESPONSE)  # Only has soil_ch1, soil_ch2

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        # Should have weather but not soil_ch3
        assert result.status == "success"
        ext_ids = [r.get("external_id") for r in result.readings]
        assert "weather" in ext_ids
        assert "soil_ch3" not in ext_ids
