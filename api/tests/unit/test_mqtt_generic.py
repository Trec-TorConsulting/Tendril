"""Tests for the generic MQTT device connector."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.integrations.connectors.mqtt_generic import (
    MqttGenericConnector,
    _coerce_numeric,
    _resolve_path,
    _topic_matches,
    extract_mapped_fields,
    validate_mqtt_topic,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── Field Mapping Engine Tests ─────────────────────────────────────────────────


class TestExtractMappedFields:
    """Test the JSON field mapping engine."""

    def test_flat_mapping(self):
        payload = {"temperature": 72.5, "humidity": 55.0}
        mapping = {"temperature": "ambient_temp_f", "humidity": "ambient_humidity"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_temp_f": 72.5, "ambient_humidity": 55.0}

    def test_nested_dot_notation(self):
        payload = {"sensor": {"temp": 72.5, "rh": 55}}
        mapping = {"sensor.temp": "ambient_temp_f", "sensor.rh": "ambient_humidity"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_temp_f": 72.5, "ambient_humidity": 55.0}

    def test_deeply_nested(self):
        payload = {"data": {"readings": {"0": {"value": 6.2}}}}
        mapping = {"data.readings.0.value": "ph"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ph": 6.2}

    def test_array_index_access(self):
        payload = {"readings": [{"value": 72.5}, {"value": 6.2}]}
        mapping = {"readings.0.value": "ambient_temp_f", "readings.1.value": "ph"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_temp_f": 72.5, "ph": 6.2}

    def test_string_coercion(self):
        payload = {"ph": "6.2", "ec": "1.8"}
        mapping = {"ph": "ph", "ec": "ec"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ph": 6.2, "ec": 1.8}

    def test_integer_values(self):
        payload = {"co2": 800, "lux": 45000}
        mapping = {"co2": "co2", "lux": "lux"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"co2": 800.0, "lux": 45000.0}

    def test_missing_fields_ignored(self):
        payload = {"temperature": 72.5}
        mapping = {"temperature": "ambient_temp_f", "humidity": "ambient_humidity"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_temp_f": 72.5}

    def test_unmapped_fields_not_included(self):
        payload = {"temperature": 72.5, "extra_field": "ignored", "another": 999}
        mapping = {"temperature": "ambient_temp_f"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_temp_f": 72.5}

    def test_non_numeric_string_ignored(self):
        payload = {"status": "online", "temp": 72.5}
        mapping = {"status": "ambient_temp_f", "temp": "ambient_temp_f"}
        result = extract_mapped_fields(payload, mapping)
        # "online" can't be coerced, but temp can
        assert result == {"ambient_temp_f": 72.5}

    def test_empty_string_ignored(self):
        payload = {"temp": "", "humidity": 55}
        mapping = {"temp": "ambient_temp_f", "humidity": "ambient_humidity"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_humidity": 55.0}

    def test_boolean_coercion(self):
        payload = {"is_on": True}
        mapping = {"is_on": "ambient_temp_f"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_temp_f": 1.0}

    def test_null_value_ignored(self):
        payload = {"temp": None, "humidity": 55}
        mapping = {"temp": "ambient_temp_f", "humidity": "ambient_humidity"}
        result = extract_mapped_fields(payload, mapping)
        assert result == {"ambient_humidity": 55.0}

    def test_empty_mapping(self):
        payload = {"temp": 72.5}
        result = extract_mapped_fields(payload, {})
        assert result == {}

    def test_empty_payload(self):
        mapping = {"temp": "ambient_temp_f"}
        result = extract_mapped_fields({}, mapping)
        assert result == {}


# ── Path Resolution Tests ──────────────────────────────────────────────────────


class TestResolvePath:
    """Test dot-notation path resolution."""

    def test_simple_key(self):
        assert _resolve_path({"temp": 72.5}, "temp") == 72.5

    def test_nested_key(self):
        assert _resolve_path({"a": {"b": {"c": 42}}}, "a.b.c") == 42

    def test_missing_key(self):
        assert _resolve_path({"temp": 72.5}, "humidity") is None

    def test_missing_nested(self):
        assert _resolve_path({"a": {"b": 1}}, "a.c.d") is None

    def test_array_index(self):
        assert _resolve_path({"items": [10, 20, 30]}, "items.1") == 20

    def test_array_out_of_bounds(self):
        assert _resolve_path({"items": [10]}, "items.5") is None

    def test_none_intermediate(self):
        assert _resolve_path({"a": None}, "a.b") is None

    def test_scalar_intermediate(self):
        assert _resolve_path({"a": 42}, "a.b") is None


# ── Numeric Coercion Tests ─────────────────────────────────────────────────────


class TestCoerceNumeric:
    """Test value-to-float coercion."""

    def test_int(self):
        assert _coerce_numeric(42) == 42.0

    def test_float(self):
        assert _coerce_numeric(3.14) == 3.14

    def test_string_float(self):
        assert _coerce_numeric("6.2") == 6.2

    def test_string_int(self):
        assert _coerce_numeric("100") == 100.0

    def test_string_with_spaces(self):
        assert _coerce_numeric("  72.5  ") == 72.5

    def test_empty_string(self):
        assert _coerce_numeric("") is None

    def test_non_numeric_string(self):
        assert _coerce_numeric("hello") is None

    def test_none(self):
        assert _coerce_numeric(None) is None

    def test_list(self):
        assert _coerce_numeric([1, 2, 3]) is None

    def test_dict(self):
        assert _coerce_numeric({"a": 1}) is None

    def test_bool_true(self):
        assert _coerce_numeric(True) == 1.0

    def test_bool_false(self):
        assert _coerce_numeric(False) == 0.0


# ── Topic Matching Tests ───────────────────────────────────────────────────────


class TestTopicMatches:
    """Test MQTT topic pattern matching."""

    def test_exact_match(self):
        assert _topic_matches("home/sensor/temp", "home/sensor/temp") is True

    def test_no_match(self):
        assert _topic_matches("home/sensor/temp", "home/sensor/humidity") is False

    def test_single_level_wildcard(self):
        assert _topic_matches("home/+/temp", "home/sensor/temp") is True
        assert _topic_matches("home/+/temp", "home/garden/temp") is True

    def test_single_level_no_match(self):
        assert _topic_matches("home/+/temp", "home/sensor/sub/temp") is False

    def test_multi_level_wildcard(self):
        assert _topic_matches("home/#", "home/sensor/temp") is True
        assert _topic_matches("home/#", "home/a/b/c") is True
        assert _topic_matches("home/#", "home") is True

    def test_multi_level_no_match(self):
        assert _topic_matches("home/#", "other/sensor") is False

    def test_combined_wildcards(self):
        assert _topic_matches("home/+/sensor/#", "home/room1/sensor/temp") is True
        assert _topic_matches("home/+/sensor/#", "home/room1/sensor/a/b") is True

    def test_different_lengths(self):
        assert _topic_matches("a/b", "a/b/c") is False
        assert _topic_matches("a/b/c", "a/b") is False


# ── Topic Validation Tests ─────────────────────────────────────────────────────


class TestValidateMqttTopic:
    """Test MQTT topic validation."""

    def test_valid_topic(self):
        assert validate_mqtt_topic("zigbee2mqtt/soil_sensor") is None

    def test_valid_with_wildcard(self):
        assert validate_mqtt_topic("zigbee2mqtt/+/state") is None

    def test_valid_with_multi_level(self):
        assert validate_mqtt_topic("home/sensors/#") is None

    def test_empty_topic(self):
        assert validate_mqtt_topic("") is not None
        assert validate_mqtt_topic("   ") is not None

    def test_forbidden_hash_alone(self):
        error = validate_mqtt_topic("#")
        assert error is not None
        assert "too broad" in error

    def test_forbidden_plus_alone(self):
        error = validate_mqtt_topic("+")
        assert error is not None
        assert "at least one specific level" in error

    def test_all_wildcards(self):
        error = validate_mqtt_topic("+/+/+")
        assert error is not None
        assert "at least one specific level" in error

    def test_hash_not_last(self):
        error = validate_mqtt_topic("home/#/temp")
        assert error is not None
        assert "last segment" in error

    def test_tendril_internal_topics_blocked(self):
        error = validate_mqtt_topic("t/abc/d/xyz/sensor/readings")
        assert error is not None
        assert "internal" in error

    def test_long_topic(self):
        error = validate_mqtt_topic("a" * 513)
        assert error is not None
        assert "512" in error


# ── Connector Integration Tests ────────────────────────────────────────────────


class TestMqttGenericConnector:
    """Test the connector's handle_webhook and persist_readings."""

    def _make_connector(self, device_maps=None):
        """Create a connector with mock config and device maps."""

        config = MagicMock()
        config.tenant_id = uuid.uuid4()
        config.id = uuid.uuid4()

        if device_maps is None:
            dm = MagicMock()
            dm.external_id = "zigbee2mqtt/soil_sensor"
            dm.enabled = True
            dm.sensor_mapping = {"temperature": "ambient_temp_f", "humidity": "ambient_humidity"}
            dm.tent_id = uuid.uuid4()
            dm.bucket_id = None
            device_maps = [dm]

        return MqttGenericConnector(config, {}, device_maps)

    async def test_handle_webhook_tent_target(self):
        connector = self._make_connector()
        payload = {
            "_topic": "zigbee2mqtt/soil_sensor",
            "_raw": {"temperature": 72.5, "humidity": 55.0},
        }
        result = await connector.handle_webhook(payload)
        assert len(result.readings) == 1
        assert result.readings[0]["ambient_temp_f"] == 72.5
        assert result.readings[0]["ambient_humidity"] == 55.0
        assert result.readings[0]["target"] == "tent"

    async def test_handle_webhook_bucket_target(self):
        dm = MagicMock()
        dm.external_id = "hydro/bucket1/sensors"
        dm.enabled = True
        dm.sensor_mapping = {"ph": "ph", "ec": "ec", "water_temp": "water_temp_f"}
        dm.tent_id = None
        dm.bucket_id = uuid.uuid4()

        connector = self._make_connector(device_maps=[dm])
        payload = {
            "_topic": "hydro/bucket1/sensors",
            "_raw": {"ph": 6.2, "ec": 1.8, "water_temp": 68.5},
        }
        result = await connector.handle_webhook(payload)
        assert len(result.readings) == 1
        assert result.readings[0]["ph"] == 6.2
        assert result.readings[0]["ec"] == 1.8
        assert result.readings[0]["target"] == "bucket"

    async def test_handle_webhook_no_matching_topic(self):
        connector = self._make_connector()
        payload = {
            "_topic": "unrelated/topic",
            "_raw": {"temperature": 72.5},
        }
        result = await connector.handle_webhook(payload)
        assert len(result.readings) == 0
        assert len(result.errors) == 1

    async def test_handle_webhook_no_sensor_mapping(self):
        dm = MagicMock()
        dm.external_id = "test/topic"
        dm.enabled = True
        dm.sensor_mapping = {}
        dm.tent_id = uuid.uuid4()
        dm.bucket_id = None

        connector = self._make_connector(device_maps=[dm])
        payload = {"_topic": "test/topic", "_raw": {"temp": 72.5}}
        result = await connector.handle_webhook(payload)
        assert len(result.readings) == 0
        assert len(result.errors) == 1
        assert "no sensor_mapping" in result.errors[0]

    async def test_handle_webhook_wildcard_match(self):
        dm = MagicMock()
        dm.external_id = "zigbee2mqtt/+/state"
        dm.enabled = True
        dm.sensor_mapping = {"temperature": "ambient_temp_f"}
        dm.tent_id = uuid.uuid4()
        dm.bucket_id = None

        connector = self._make_connector(device_maps=[dm])
        payload = {
            "_topic": "zigbee2mqtt/sensor_1/state",
            "_raw": {"temperature": 72.5},
        }
        result = await connector.handle_webhook(payload)
        assert len(result.readings) == 1

    async def test_handle_webhook_non_dict_payload(self):
        connector = self._make_connector()
        payload = {"_topic": "zigbee2mqtt/soil_sensor", "_raw": "not a dict"}
        result = await connector.handle_webhook(payload)
        assert len(result.readings) == 0
        assert len(result.errors) == 1

    async def test_poll_returns_empty(self):
        connector = self._make_connector()
        result = await connector.poll()
        assert len(result.readings) == 0
        assert len(result.errors) == 0

    async def test_discover_returns_empty(self):
        connector = self._make_connector()
        devices = await connector.discover_devices()
        assert devices == []
