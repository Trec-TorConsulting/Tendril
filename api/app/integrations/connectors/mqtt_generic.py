"""Generic MQTT device connector.

Allows users to connect any MQTT-speaking device by configuring:
  - A topic to subscribe to (per device map's external_id)
  - A JSON field mapping (device map's sensor_mapping) from payload fields → Tendril fields

Config schema (encrypted on IntegrationConfig):
  {
    "description": "Optional description of what this integration covers"
  }

Device map config:
  - external_id: The MQTT topic to subscribe to (e.g., "zigbee2mqtt/soil_sensor_1")
  - sensor_mapping: Dict mapping source payload fields → Tendril sensor fields
    e.g., {"temperature": "ambient_temp_f", "humidity": "ambient_humidity", "sensor.ph": "ph"}
  - tent_id or bucket_id: Target for persisted readings

Supports:
  - Flat JSON payloads: {"temp": 72.5, "rh": 55}
  - Nested JSON with dot-notation: {"sensor": {"temp": 72.5}} → mapping "sensor.temp"
  - String-to-number coercion: {"ph": "6.2"} → 6.2
  - Arrays ignored (only scalar values mapped)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import BucketSensorReading, TentSensorReading
from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector

logger = logging.getLogger(__name__)


# Dangerous topic patterns that could subscribe to everything
_FORBIDDEN_TOPICS = {"#", "+", "$SYS/#", "$SYS/+"}


@register_connector
class MqttGenericConnector(BaseConnector):
    """Generic MQTT device connector — maps arbitrary MQTT JSON to sensor readings."""

    integration_type = "mqtt_generic"

    async def poll(self) -> ConnectorResult:
        """No-op — generic MQTT is push-based, not polled."""
        return ConnectorResult()

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Process an MQTT message payload for a specific device map.

        Called by the MQTT subscription manager when a message arrives on a
        topic matching one of this integration's device maps.

        The payload dict should contain:
          - "_topic": The MQTT topic the message arrived on
          - "_raw": The raw parsed JSON payload from the device
          - "_device_map_id": UUID of the matched device map (optional)
        """
        result = ConnectorResult()

        raw_payload = payload.get("_raw", payload)
        topic = payload.get("_topic", "")

        if not raw_payload or not isinstance(raw_payload, dict):
            result.errors.append(f"Non-dict payload on topic {topic}")
            return result

        # Find matching device map by topic (external_id = topic)
        matched_maps = [dm for dm in self.device_maps if dm.external_id == topic and dm.enabled]

        if not matched_maps:
            # Try wildcard matching (+ single level, # multi level)
            matched_maps = [dm for dm in self.device_maps if dm.enabled and _topic_matches(dm.external_id, topic)]

        if not matched_maps:
            result.errors.append(f"No device map matches topic: {topic}")
            return result

        for dm in matched_maps:
            mapping = dm.sensor_mapping or {}
            if not mapping:
                result.errors.append(f"Device map {dm.external_id} has no sensor_mapping configured")
                continue

            reading = extract_mapped_fields(raw_payload, mapping)
            if not reading:
                continue

            reading["tenant_id"] = str(self.config.tenant_id)
            reading["external_id"] = dm.external_id

            if dm.bucket_id:
                reading["target"] = "bucket"
                reading["bucket_id"] = str(dm.bucket_id)
            elif dm.tent_id:
                reading["target"] = "tent"
                reading["tent_id"] = str(dm.tent_id)
            else:
                result.errors.append(f"Device map {dm.external_id} has no tent_id or bucket_id")
                continue

            result.readings.append(reading)

        return result

    async def persist_readings(self, session: AsyncSession, result: ConnectorResult) -> int:
        """Write mapped readings to TentSensorReading or BucketSensorReading."""
        count = 0
        now = datetime.now(UTC)

        for reading in result.readings:
            target = reading.get("target")
            tenant_id = reading.get("tenant_id")
            external_id = reading.get("external_id", "mqtt_generic")

            if target == "bucket":
                bucket_id = reading.get("bucket_id")
                if not bucket_id or not tenant_id:
                    continue

                row = BucketSensorReading(
                    tenant_id=tenant_id,
                    bucket_id=bucket_id,
                    device_id=f"mqtt:{external_id}",
                    ph=reading.get("ph"),
                    ec=reading.get("ec"),
                    ppm=reading.get("ppm"),
                    water_temp_f=reading.get("water_temp_f"),
                    water_level_pct=reading.get("water_level_pct"),
                    dissolved_oxygen=reading.get("dissolved_oxygen"),
                    flow_rate=reading.get("flow_rate"),
                    orp=reading.get("orp"),
                    recorded_at=now,
                )
                session.add(row)
                count += 1

            elif target == "tent":
                tent_id = reading.get("tent_id")
                if not tent_id or not tenant_id:
                    continue

                row = TentSensorReading(
                    tenant_id=tenant_id,
                    tent_id=tent_id,
                    device_id=f"mqtt:{external_id}",
                    ambient_temp_f=reading.get("ambient_temp_f"),
                    ambient_humidity=reading.get("ambient_humidity"),
                    vpd=reading.get("vpd"),
                    co2=reading.get("co2"),
                    lux=reading.get("lux"),
                    par_ppfd=reading.get("par_ppfd"),
                    recorded_at=now,
                )
                session.add(row)
                count += 1

        return count

    async def discover_devices(self) -> list:
        """No-op — generic MQTT devices aren't discoverable."""
        return []


# ── Field Mapping Engine ───────────────────────────────────────────────────────


def extract_mapped_fields(payload: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    """Extract and map fields from a JSON payload using the sensor_mapping config.

    Args:
        payload: The raw JSON payload from the MQTT message.
        mapping: Dict of {source_field: tendril_field}.
            Source field supports dot-notation for nested access (e.g., "sensor.temp").

    Returns:
        Dict of {tendril_field: numeric_value} with only successfully mapped fields.
    """
    result: dict[str, Any] = {}

    for source_path, tendril_field in mapping.items():
        value = _resolve_path(payload, source_path)
        if value is None:
            continue

        numeric = _coerce_numeric(value)
        if numeric is not None:
            result[tendril_field] = numeric

    return result


def _resolve_path(payload: dict[str, Any], path: str) -> Any:
    """Resolve a dot-notation path in a nested dict.

    "temperature" → payload["temperature"]
    "sensor.temp" → payload["sensor"]["temp"]
    "data.readings.0.value" → payload["data"]["readings"][0]["value"]
    """
    parts = path.split(".")
    current: Any = payload

    for part in parts:
        if current is None:
            return None

        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx] if 0 <= idx < len(current) else None
            except ValueError, IndexError:
                return None
        else:
            return None

    return current


def _coerce_numeric(value: Any) -> float | None:
    """Coerce a value to float. Returns None for non-numeric values."""
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    if isinstance(value, bool):
        return float(value)
    return None


# ── Topic Matching ─────────────────────────────────────────────────────────────


def _topic_matches(pattern: str, topic: str) -> bool:
    """Check if an MQTT topic matches a subscription pattern.

    Supports MQTT wildcards:
      + matches exactly one level
      # matches zero or more levels (must be last)
    """
    pattern_parts = pattern.split("/")
    topic_parts = topic.split("/")

    for i, p_part in enumerate(pattern_parts):
        if p_part == "#":
            return True  # # matches everything from here
        if i >= len(topic_parts):
            return False
        if p_part == "+":
            continue  # + matches any single level
        if p_part != topic_parts[i]:
            return False

    return len(pattern_parts) == len(topic_parts)


def validate_mqtt_topic(topic: str) -> str | None:
    """Validate an MQTT topic for use as a subscription.

    Returns None if valid, or an error message if invalid.
    """
    if not topic or not topic.strip():
        return "Topic cannot be empty"

    topic = topic.strip()

    if topic in _FORBIDDEN_TOPICS:
        return f"Topic '{topic}' is too broad — would subscribe to all messages"

    if len(topic) > 512:
        return "Topic must be 512 characters or fewer"

    # Must have at least one non-wildcard level
    parts = topic.split("/")
    non_wildcard = [p for p in parts if p not in ("+", "#")]
    if not non_wildcard:
        return "Topic must contain at least one specific level (not just wildcards)"

    # # must be the last part if present
    if "#" in parts and parts[-1] != "#":
        return "Multi-level wildcard (#) must be the last segment"

    # Prevent subscribing to Tendril internal topics
    if parts[0] == "t" and len(parts) >= 4 and parts[2] == "d":
        return "Cannot subscribe to Tendril internal device topics (t/+/d/+/...)"

    return None
