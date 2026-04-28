"""Tests for the OpenWeather integration connector."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
import pytest
from app.integrations.connectors.base import ConnectorResult, get_connector_class
from app.integrations.connectors.openweather import (
    DiscoveredDevice,
    OpenWeatherConfig,
    OpenWeatherConnector,
    write_openweather_readings,
)
from app.integrations.models import IntegrationConfig, IntegrationDeviceMap

pytestmark = pytest.mark.asyncio(loop_scope="session")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_REQUEST_CURRENT = httpx.Request("GET", "https://api.openweathermap.org/data/2.5/weather")
_FAKE_REQUEST_FORECAST = httpx.Request("GET", "https://api.openweathermap.org/data/2.5/forecast")
_FAKE_REQUEST_ONECALL = httpx.Request("GET", "https://api.openweathermap.org/data/3.0/onecall")


def _resp(status_code: int = 200, json: Any = None, request: httpx.Request | None = None) -> httpx.Response:
    r = httpx.Response(status_code, json=json or {})
    r._request = request or _FAKE_REQUEST_CURRENT
    return r


# Sample API responses

_CURRENT_25 = {
    "main": {"temp": 22.5, "humidity": 65, "pressure": 1013},
    "wind": {"speed": 5.2},
    "weather": [{"id": 800, "description": "clear sky"}],
    "rain": {"1h": 0.5},
}

_FORECAST_25 = {
    "list": [
        {
            "dt_txt": "2026-04-29 12:00:00",
            "main": {"temp": 24.0},
            "wind": {"speed": 4.0},
            "rain": {"3h": 1.2},
            "weather": [{"id": 500}],
        },
        {
            "dt_txt": "2026-04-29 15:00:00",
            "main": {"temp": 26.0},
            "wind": {"speed": 6.0},
            "rain": {"3h": 0.0},
            "weather": [{"id": 801}],
        },
        {
            "dt_txt": "2026-04-30 12:00:00",
            "main": {"temp": 20.0},
            "wind": {"speed": 8.0},
            "rain": {"3h": 5.0},
            "weather": [{"id": 502}],
        },
    ]
}

_ONECALL_30 = {
    "current": {
        "temp": 23.1,
        "humidity": 60,
        "pressure": 1015,
        "wind_speed": 4.5,
        "uvi": 6.5,
        "dew_point": 14.2,
        "weather": [{"id": 801}],
        "rain": {"1h": 0.3},
    },
    "daily": [
        {
            "dt": 1745971200,
            "temp": {"max": 28.0, "min": 15.0},
            "rain": 3.5,
            "wind_speed": 7.0,
            "uvi": 8.0,
            "weather": [{"id": 500}],
        },
    ],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(tenant_id, **overrides) -> IntegrationConfig:
    return IntegrationConfig(
        id=overrides.pop("id", uuid4()),
        tenant_id=tenant_id,
        type="openweather",
        name="Test OpenWeather",
        config="encrypted-placeholder",
        webhook_secret="test-secret",
        enabled=True,
        poll_interval_s=1800,
    )


def _make_device_map(
    tenant_id,
    integration_id,
    external_id: str = "47.6,-122.3",
    tent_id=None,
) -> IntegrationDeviceMap:
    return IntegrationDeviceMap(
        id=uuid4(),
        tenant_id=tenant_id,
        integration_id=integration_id,
        external_id=external_id,
        external_name=f"Location {external_id}",
        tent_id=tent_id or uuid4(),
        bucket_id=None,
        sensor_mapping={},
        enabled=True,
    )


def _make_connector(tenant_id, decrypted_config=None, device_maps=None):
    cfg = _make_config(tenant_id)
    dc = decrypted_config or {"api_key": "test-api-key-12345"}
    dm = device_maps if device_maps is not None else [_make_device_map(tenant_id, cfg.id)]
    return OpenWeatherConnector(config=cfg, decrypted_config=dc, device_maps=dm)


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


class TestOpenWeatherConfig:
    def test_valid_config(self):
        cfg = OpenWeatherConfig(api_key="abcdef1234567890")
        assert cfg.api_key == "abcdef1234567890"
        assert cfg.use_onecall_30 is False

    def test_short_api_key_rejected(self):
        with pytest.raises(Exception):
            OpenWeatherConfig(api_key="short")

    def test_onecall_flag(self):
        cfg = OpenWeatherConfig(api_key="abcdef1234567890", use_onecall_30=True)
        assert cfg.use_onecall_30 is True


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_connector_registered(self):
        cls = get_connector_class("openweather")
        assert cls is OpenWeatherConnector


# ---------------------------------------------------------------------------
# Polling — 2.5 free tier
# ---------------------------------------------------------------------------


class TestPoll25:
    async def test_poll_success(self):
        connector = _make_connector(uuid4())

        async def mock_get(url, **kwargs):
            if "/data/2.5/weather" in url:
                return _resp(200, _CURRENT_25, _FAKE_REQUEST_CURRENT)
            if "/data/2.5/forecast" in url:
                return _resp(200, _FORECAST_25, _FAKE_REQUEST_FORECAST)
            return _resp(404)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "success"
        assert result.readings_count == 1
        r = result.readings[0]
        assert r["temperature_c"] == 22.5
        assert r["humidity_pct"] == 65
        assert r["pressure_hpa"] == 1013
        assert r["precipitation_mm"] == 0.5
        # Wind: 5.2 m/s * 3.6 = 18.72 km/h
        assert abs(r["wind_speed_kmh"] - 18.72) < 0.1
        assert r["weather_code"] == 800
        assert r["forecast"] is not None
        assert len(r["forecast"]) == 2  # Two days

    async def test_poll_no_device_maps(self):
        connector = _make_connector(uuid4(), device_maps=[])
        result = await connector.poll()
        assert result.status == "success"
        assert result.readings_count == 0

    async def test_poll_invalid_external_id(self):
        tid = uuid4()
        cfg = _make_config(tid)
        dm = _make_device_map(tid, cfg.id, external_id="bad-format")
        connector = OpenWeatherConnector(
            config=cfg, decrypted_config={"api_key": "test12345678"}, device_maps=[dm]
        )

        async def mock_get(url, **kwargs):
            return _resp(200, _CURRENT_25)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "error"
        assert "Invalid external_id" in result.errors[0]


# ---------------------------------------------------------------------------
# Polling — One Call 3.0
# ---------------------------------------------------------------------------


class TestPoll30:
    async def test_poll_onecall_success(self):
        connector = _make_connector(
            uuid4(),
            decrypted_config={"api_key": "test-key-12345", "use_onecall_30": True},
        )

        async def mock_get(url, **kwargs):
            if "/data/3.0/onecall" in url:
                return _resp(200, _ONECALL_30, _FAKE_REQUEST_ONECALL)
            return _resp(404)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "success"
        assert result.readings_count == 1
        r = result.readings[0]
        assert r["temperature_c"] == 23.1
        assert r["uv_index"] == 6.5
        assert r["dew_point_c"] == 14.2
        assert r["forecast"] is not None


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrors:
    async def test_auth_failure(self):
        connector = _make_connector(uuid4())

        async def mock_get(url, **kwargs):
            return _resp(401, {"message": "Invalid API key"}, _FAKE_REQUEST_CURRENT)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "error"
        assert "authentication failed" in result.errors[0]

    async def test_rate_limit(self):
        connector = _make_connector(uuid4())

        async def mock_get(url, **kwargs):
            return _resp(429, {}, _FAKE_REQUEST_CURRENT)

        with patch.object(connector, "_client") as mock_client:
            ctx = AsyncMock()
            ctx.get = AsyncMock(side_effect=mock_get)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = ctx

            result = await connector.poll()

        assert result.status == "error"
        assert "rate limit" in result.errors[0]

    async def test_network_error(self):
        connector = _make_connector(uuid4())

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
# Webhook (not supported)
# ---------------------------------------------------------------------------


class TestWebhook:
    async def test_webhook_rejected(self):
        connector = _make_connector(uuid4())
        result = await connector.handle_webhook({"data": "test"})
        assert result.status == "error"
        assert "does not support webhooks" in result.errors[0]


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class TestDiscovery:
    async def test_discover_returns_empty(self):
        connector = _make_connector(uuid4())
        devices = await connector.discover_devices()
        assert devices == []


# ---------------------------------------------------------------------------
# Dew point calculation
# ---------------------------------------------------------------------------


class TestDewPoint:
    def test_dew_point_calculation(self):
        dp = OpenWeatherConnector._calc_dew_point(20.0, 60.0)
        assert dp is not None
        assert 11.0 < dp < 13.0

    def test_dew_point_none_inputs(self):
        assert OpenWeatherConnector._calc_dew_point(None, 60.0) is None
        assert OpenWeatherConnector._calc_dew_point(20.0, None) is None
        assert OpenWeatherConnector._calc_dew_point(20.0, 0) is None


# ---------------------------------------------------------------------------
# Daily forecast builder
# ---------------------------------------------------------------------------


class TestForecastBuilder:
    def test_aggregate_daily(self):
        connector = _make_connector(uuid4())
        result = connector._build_daily_forecast(_FORECAST_25)
        assert len(result) == 2
        day1 = result[0]
        assert day1["date"] == "2026-04-29"
        assert day1["temp_max_c"] == 26.0
        assert day1["temp_min_c"] == 24.0
        assert day1["precipitation_mm"] == 1.2

    def test_empty_forecast(self):
        connector = _make_connector(uuid4())
        result = connector._build_daily_forecast({"list": []})
        assert result == []


# ---------------------------------------------------------------------------
# ConnectorResult
# ---------------------------------------------------------------------------


class TestConnectorResult:
    def test_success(self):
        r = ConnectorResult()
        r.readings.append({"data": 1})
        assert r.status == "success"

    def test_partial(self):
        r = ConnectorResult()
        r.readings.append({"data": 1})
        r.errors.append("oops")
        assert r.status == "partial"

    def test_error(self):
        r = ConnectorResult()
        r.errors.append("fail")
        assert r.status == "error"
