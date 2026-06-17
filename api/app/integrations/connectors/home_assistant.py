"""Home Assistant Bridge connector.

Polls HA REST API for entity states and maps them to Tendril sensor readings.
Can also call HA services for automation (e.g., toggle fans/pumps).

Config schema (encrypted):
  {
    "base_url": "http://192.168.x.x:8123",
    "token": "long-lived-access-token"
  }

Device map external_id format: "sensor.tent_temperature" (HA entity_id)
Device map sensor_mapping: {"state": "ambient_temp_f"} or auto-mapped by device_class
"""

from __future__ import annotations

import contextlib
import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import BucketSensorReading, TentSensorReading
from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector
from app.integrations.connectors.retry import retry_request

logger = logging.getLogger(__name__)

# HA device_class → Tendril field auto-mapping
_DEVICE_CLASS_MAP_TENT: dict[str, str] = {
    "temperature": "ambient_temp_f",
    "humidity": "ambient_humidity",
    "illuminance": "lux",
    "carbon_dioxide": "co2",
    "volatile_organic_compounds": "voc",
    "atmospheric_pressure": "air_pressure",
}

_DEVICE_CLASS_MAP_BUCKET: dict[str, str] = {
    "ph": "ph",
    "conductivity": "ec",
    "moisture": "water_level_pct",
}


@register_connector
class HomeAssistantConnector(BaseConnector):
    integration_type = "home_assistant"

    @property
    def base_url(self) -> str:
        return self.decrypted_config["base_url"].rstrip("/")

    @property
    def token(self) -> str:
        return self.decrypted_config["token"]

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def poll(self) -> ConnectorResult:
        """Fetch current state for all mapped HA entities."""
        result = ConnectorResult()

        if not self.device_maps:
            return result

        async with httpx.AsyncClient(timeout=15) as client:
            for dm in self.device_maps:
                if not dm.enabled:
                    continue
                entity_id = dm.external_id
                try:
                    resp = await retry_request(
                                lambda url=f"{self.base_url}/api/states/{entity_id}": client.get(  # type: ignore[misc]
                            url,
                            headers=self.headers,
                        ),
                        description=f"home_assistant.poll {entity_id}",
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        reading = self._map_entity_to_reading(data, dm)
                        if reading:
                            result.readings.append(reading)
                    elif resp.status_code == 404:
                        result.errors.append(f"Entity not found: {entity_id}")
                    else:
                        result.errors.append(f"HA API error for {entity_id}: {resp.status_code}")
                except httpx.RequestError as e:
                    result.errors.append(f"Connection error for {entity_id}: {e!s}")

        return result

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Handle HA webhook automation pushes (optional — HA can send state changes)."""
        result = ConnectorResult()

        entity_id = payload.get("entity_id")
        state = payload.get("state")
        if not entity_id:
            result.errors.append("Missing entity_id in webhook payload")
            return result

        # Find matching device map
        dm = next((m for m in self.device_maps if m.external_id == entity_id and m.enabled), None)
        if dm is None:
            result.errors.append(f"No device map for entity: {entity_id}")
            return result

        data = {
            "entity_id": entity_id,
            "state": state,
            "attributes": payload.get("attributes", {}),
        }
        reading = self._map_entity_to_reading(data, dm)
        if reading:
            result.readings.append(reading)

        return result

    async def persist_readings(self, session: AsyncSession, result: ConnectorResult) -> int:
        """Write HA readings to TentSensorReading or BucketSensorReading."""
        count = 0
        now = datetime.now(UTC)

        for reading in result.readings:
            target = reading.get("target")
            tenant_id = reading.get("tenant_id")
            external_id = reading.get("external_id", "ha")

            if target == "tent":
                tent_id = reading.get("tent_id")
                if not tent_id or not tenant_id:
                    continue

                row = TentSensorReading(
                    tenant_id=tenant_id,
                    tent_id=tent_id,
                    device_id=f"ha:{external_id}",
                    ambient_temp_f=reading.get("ambient_temp_f"),
                    ambient_humidity=reading.get("ambient_humidity"),
                    vpd=reading.get("vpd"),
                    co2=reading.get("co2"),
                    lux=reading.get("lux"),
                    par_ppfd=reading.get("par_ppfd"),
                    air_pressure=reading.get("air_pressure"),
                    voc=reading.get("voc"),
                    recorded_at=now,
                )
                session.add(row)
                count += 1

            elif target == "bucket":
                bucket_id = reading.get("bucket_id")
                if not bucket_id or not tenant_id:
                    continue

                row = BucketSensorReading(  # type: ignore[assignment]
                    tenant_id=tenant_id,
                    bucket_id=bucket_id,
                    device_id=f"ha:{external_id}",
                    ph=reading.get("ph"),
                    ec=reading.get("ec"),
                    water_temp_f=reading.get("water_temp_f"),
                    water_level_pct=reading.get("water_level_pct"),
                    recorded_at=now,
                )
                session.add(row)
                count += 1

        return count

    async def discover_devices(self) -> list[dict[str, Any]]:
        """Discover all HA entities suitable for grow monitoring."""
        relevant_domains = {"sensor", "binary_sensor", "switch", "light", "fan", "climate"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await retry_request(
                    lambda: client.get(f"{self.base_url}/api/states", headers=self.headers),
                    description="home_assistant.discover_devices",
                )
                resp.raise_for_status()
                entities = resp.json()
        except Exception as e:
            logger.warning("HA discovery failed: %s", e)
            return []

        discovered = []
        for entity in entities:
            entity_id = entity.get("entity_id", "")
            domain = entity_id.split(".")[0] if "." in entity_id else ""

            if domain not in relevant_domains:
                continue

            attrs = entity.get("attributes", {})
            discovered.append(
                {
                    "external_id": entity_id,
                    "name": attrs.get("friendly_name", entity_id),
                    "device_type": attrs.get("device_class", domain),
                    "state": entity.get("state"),
                    "unit": attrs.get("unit_of_measurement"),
                }
            )

        return discovered

    async def call_service(self, domain: str, service: str, data: dict[str, Any] | None = None) -> dict:
        """Call a Home Assistant service (e.g., switch.turn_on).

        Used by Tendril automation rules to control devices via HA.
        """
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await retry_request(
                lambda: client.post(
                    f"{self.base_url}/api/services/{domain}/{service}",
                    headers=self.headers,
                    json=data or {},
                ),
                description=f"home_assistant.call_service {domain}.{service}",
            )
            resp.raise_for_status()
            return resp.json()

    async def test_connection(self) -> dict[str, Any]:
        """Test connectivity to HA instance.

        Intentionally does NOT use ``retry_request`` — this endpoint
        is called from the UI's 'Test connection' button and the user
        is waiting for a verdict. Surfacing the first failure quickly
        is better UX than spending up to ~7s retrying.
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/", headers=self.headers)
                resp.raise_for_status()
                data = resp.json()
                return {"reachable": True, "message": data.get("message", "OK")}
        except httpx.ConnectError:
            return {"reachable": False, "message": f"Cannot connect to {self.base_url}"}
        except httpx.TimeoutException:
            return {"reachable": False, "message": "Connection timed out"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {"reachable": False, "message": "Invalid access token (401 Unauthorized)"}
            return {"reachable": False, "message": f"HTTP error: {e.response.status_code}"}

    # ── Private Helpers ────────────────────────────────────────────────────

    def _map_entity_to_reading(self, entity_data: dict, dm: Any) -> dict[str, Any] | None:
        """Map a HA entity state response to a Tendril reading dict.

        Uses sensor_mapping from device map if configured,
        otherwise falls back to device_class auto-mapping.
        """
        entity_id = entity_data.get("entity_id", dm.external_id)
        state = entity_data.get("state")
        attrs = entity_data.get("attributes", {})

        # Skip unavailable/unknown states
        if state in ("unavailable", "unknown", None):
            return None

        # Try to get numeric value
        try:
            numeric = float(state) if state is not None else None
        except (ValueError, TypeError):
            numeric = None

        reading: dict[str, Any] = {
            "external_id": entity_id,
            "tenant_id": str(self.config.tenant_id),
        }

        # Set target
        if dm.bucket_id:
            reading["target"] = "bucket"
            reading["bucket_id"] = str(dm.bucket_id)
        elif dm.tent_id:
            reading["target"] = "tent"
            reading["tent_id"] = str(dm.tent_id)
        else:
            return None

        # Apply custom sensor_mapping if configured
        custom_mapping = dm.sensor_mapping or {}
        if custom_mapping and numeric is not None:
            for source_key, tendril_field in custom_mapping.items():
                if source_key == "state":
                    reading[tendril_field] = numeric
                elif source_key in attrs:
                    with contextlib.suppress(ValueError, TypeError):
                        reading[tendril_field] = float(attrs[source_key])
            if len(reading) > 4:  # Has at least one mapped field
                return reading

        # Fallback: auto-map by device_class
        device_class = attrs.get("device_class", "")
        if numeric is not None:
            target = reading.get("target")
            field_map = _DEVICE_CLASS_MAP_TENT if target == "tent" else _DEVICE_CLASS_MAP_BUCKET
            tendril_field = field_map.get(device_class)
            if tendril_field:
                # Handle unit conversion for temperature (HA may send °C)
                unit = attrs.get("unit_of_measurement", "")
                if tendril_field == "ambient_temp_f" and unit == "°C":
                    numeric = numeric * 9 / 5 + 32
                reading[tendril_field] = numeric
                return reading

        # If we have a numeric value but no mapping, store with explicit mapping required
        if numeric is not None and custom_mapping:
            # Custom mapping was set but didn't match — skip
            return None

        return None
