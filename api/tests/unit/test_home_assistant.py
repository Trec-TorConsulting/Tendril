"""Tests for the Home Assistant bridge connector."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.integrations.connectors.home_assistant import (
    _DEVICE_CLASS_MAP_BUCKET,
    _DEVICE_CLASS_MAP_TENT,
    HomeAssistantConnector,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


def _make_connector(device_maps=None):
    """Create a connector with mock config and device maps."""
    config = MagicMock()
    config.tenant_id = uuid.uuid4()
    config.id = uuid.uuid4()
    config.encrypted_config = ""

    decrypted = {
        "base_url": "http://192.168.1.100:8123",
        "token": "test-token-do-not-use",
    }

    if device_maps is None:
        dm = MagicMock()
        dm.external_id = "sensor.tent_temperature"
        dm.enabled = True
        dm.sensor_mapping = {"state": "ambient_temp_f"}
        dm.tent_id = uuid.uuid4()
        dm.bucket_id = None
        device_maps = [dm]

    return HomeAssistantConnector(config, decrypted, device_maps)


class TestHomeAssistantProperties:
    """Test connector property resolution."""

    def test_base_url_strips_trailing_slash(self):
        connector = _make_connector()
        connector.decrypted_config["base_url"] = "http://ha.local:8123/"
        assert connector.base_url == "http://ha.local:8123"

    def test_headers_include_bearer_token(self):
        connector = _make_connector()
        assert "Authorization" in connector.headers
        assert connector.headers["Authorization"] == "Bearer test-token-do-not-use"


class TestHomeAssistantPoll:
    """Test the poll() method."""

    @patch("httpx.AsyncClient.get")
    async def test_poll_success_tent_sensor(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "entity_id": "sensor.tent_temperature",
            "state": "72.5",
            "attributes": {
                "device_class": "temperature",
                "unit_of_measurement": "°F",
                "friendly_name": "Tent Temperature",
            },
        }
        mock_get.return_value = mock_resp

        connector = _make_connector()
        result = await connector.poll()

        assert len(result.readings) == 1
        assert result.readings[0]["ambient_temp_f"] == 72.5
        assert result.readings[0]["target"] == "tent"

    @patch("httpx.AsyncClient.get")
    async def test_poll_celsius_conversion(self, mock_get):
        dm = MagicMock()
        dm.external_id = "sensor.temp_c"
        dm.enabled = True
        dm.sensor_mapping = {}  # rely on auto-mapping
        dm.tent_id = uuid.uuid4()
        dm.bucket_id = None

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "entity_id": "sensor.temp_c",
            "state": "22.5",
            "attributes": {
                "device_class": "temperature",
                "unit_of_measurement": "°C",
            },
        }
        mock_get.return_value = mock_resp

        connector = _make_connector(device_maps=[dm])
        result = await connector.poll()

        assert len(result.readings) == 1
        # 22.5°C = 72.5°F
        assert abs(result.readings[0]["ambient_temp_f"] - 72.5) < 0.01

    @patch("httpx.AsyncClient.get")
    async def test_poll_entity_not_found(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        connector = _make_connector()
        result = await connector.poll()

        assert len(result.readings) == 0
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]

    @patch("httpx.AsyncClient.get")
    async def test_poll_unavailable_state_skipped(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "entity_id": "sensor.offline",
            "state": "unavailable",
            "attributes": {"device_class": "temperature"},
        }
        mock_get.return_value = mock_resp

        connector = _make_connector()
        result = await connector.poll()
        assert len(result.readings) == 0

    @patch("httpx.AsyncClient.get")
    async def test_poll_bucket_target(self, mock_get):
        dm = MagicMock()
        dm.external_id = "sensor.reservoir_ph"
        dm.enabled = True
        dm.sensor_mapping = {"state": "ph"}
        dm.tent_id = None
        dm.bucket_id = uuid.uuid4()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "entity_id": "sensor.reservoir_ph",
            "state": "6.2",
            "attributes": {"device_class": "ph"},
        }
        mock_get.return_value = mock_resp

        connector = _make_connector(device_maps=[dm])
        result = await connector.poll()

        assert len(result.readings) == 1
        assert result.readings[0]["ph"] == 6.2
        assert result.readings[0]["target"] == "bucket"

    async def test_poll_empty_device_maps(self):
        connector = _make_connector(device_maps=[])
        result = await connector.poll()
        assert len(result.readings) == 0
        assert len(result.errors) == 0


class TestHomeAssistantWebhook:
    """Test the handle_webhook() method."""

    async def test_webhook_with_matching_entity(self):
        connector = _make_connector()
        payload = {
            "entity_id": "sensor.tent_temperature",
            "state": "75.0",
            "attributes": {"device_class": "temperature", "unit_of_measurement": "°F"},
        }
        result = await connector.handle_webhook(payload)
        assert len(result.readings) == 1
        assert result.readings[0]["ambient_temp_f"] == 75.0

    async def test_webhook_missing_entity_id(self):
        connector = _make_connector()
        result = await connector.handle_webhook({"state": "75.0"})
        assert len(result.errors) == 1
        assert "Missing entity_id" in result.errors[0]

    async def test_webhook_unmatched_entity(self):
        connector = _make_connector()
        payload = {
            "entity_id": "sensor.unknown_entity",
            "state": "42",
            "attributes": {},
        }
        result = await connector.handle_webhook(payload)
        assert len(result.errors) == 1
        assert "No device map" in result.errors[0]


class TestHomeAssistantCallService:
    """Test the call_service() method."""

    @patch("httpx.AsyncClient.post")
    async def test_call_service_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{"entity_id": "switch.fan", "state": "on"}]
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        connector = _make_connector()
        result = await connector.call_service("switch", "turn_on", {"entity_id": "switch.fan"})

        assert isinstance(result, list)
        mock_post.assert_called_once()


class TestHomeAssistantDiscovery:
    """Test the discover_devices() method."""

    @patch("httpx.AsyncClient.get")
    async def test_discover_filters_relevant_domains(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {
                "entity_id": "sensor.temp",
                "state": "72",
                "attributes": {"friendly_name": "Temp", "device_class": "temperature"},
            },
            {"entity_id": "switch.fan", "state": "off", "attributes": {"friendly_name": "Fan"}},
            {"entity_id": "automation.morning", "state": "on", "attributes": {"friendly_name": "Morning"}},
            {"entity_id": "person.admin", "state": "home", "attributes": {"friendly_name": "Admin"}},
        ]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        connector = _make_connector()
        devices = await connector.discover_devices()

        # Should include sensor and switch, exclude automation and person
        entity_ids = [d["external_id"] for d in devices]
        assert "sensor.temp" in entity_ids
        assert "switch.fan" in entity_ids
        assert "automation.morning" not in entity_ids
        assert "person.admin" not in entity_ids


class TestHomeAssistantTestConnection:
    """Test the test_connection() method."""

    @patch("httpx.AsyncClient.get")
    async def test_connection_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"message": "API running."}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        connector = _make_connector()
        result = await connector.test_connection()
        assert result["reachable"] is True


class TestDeviceClassMaps:
    """Verify device class mappings are comprehensive."""

    def test_tent_map_covers_essentials(self):
        assert "temperature" in _DEVICE_CLASS_MAP_TENT
        assert "humidity" in _DEVICE_CLASS_MAP_TENT
        assert "carbon_dioxide" in _DEVICE_CLASS_MAP_TENT

    def test_bucket_map_covers_essentials(self):
        assert "ph" in _DEVICE_CLASS_MAP_BUCKET
        assert "conductivity" in _DEVICE_CLASS_MAP_BUCKET
