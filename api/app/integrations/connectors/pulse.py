"""Pulse Grow connector — polls api.pulsegrow.com for environment data.

Supports Pulse One, Pulse Pro, and Pulse Hub devices. Maps ambient
readings (temp, humidity, VPD, CO2, lux, dew point, PAR, pressure, VOC)
to TentSensorReading, and Hub sensor readings (soil moisture, pH, EC)
to BucketSensorReading.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import BucketSensorReading, TentSensorReading
from app.integrations.connectors.base import (
    BaseConnector,
    ConnectorResult,
    propagate_header_bucket_readings,
    register_connector,
)
from app.integrations.connectors.retry import retry_request
from app.integrations.models import IntegrationDeviceMap

logger = logging.getLogger("tendril.integrations.pulse")

_TIMEOUT = 30.0
_DEFAULT_BASE_URL = "https://api.pulsegrow.com"

# Pulse device fields → TentSensorReading columns
_DEVICE_FIELD_MAP: dict[str, str] = {
    "temperatureF": "ambient_temp_f",
    "humidityRh": "ambient_humidity",
    "vpd": "vpd",
    "co2": "co2",
    "lightLux": "lux",
    "dpF": "dew_point_f",
    "par": "par_ppfd",
    "airPressure": "air_pressure",
    "voc": "voc",
}

# Hub sensor dataPointValues type IDs → BucketSensorReading columns
# These are common Pulse Hub sensor types; map by name/type if known.
_HUB_SENSOR_FIELD_MAP: dict[str, str] = {
    "soil_moisture": "soil_moisture",
    "soil_temp": "soil_temp",
    "ph": "ph",
    "ec": "ec",
    "water_temp": "water_temp_f",
}


# ---------------------------------------------------------------------------
# Config schema
# ---------------------------------------------------------------------------


class PulseConfig(BaseModel):
    """Validated config shape for Pulse Grow integrations."""

    api_key: str = Field(..., min_length=10, description="Pulse Grow API key from app.pulsegrow.com/account")
    base_url: str = Field(default=_DEFAULT_BASE_URL, description="Pulse API base URL")


# ---------------------------------------------------------------------------
# Discovery response
# ---------------------------------------------------------------------------


class DiscoveredDevice(BaseModel):
    external_id: str
    name: str
    device_type: str  # "pulse_one", "pulse_pro", "hub_sensor"
    latest_reading: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


@register_connector
class PulseConnector(BaseConnector):
    """Connector for Pulse Grow REST API."""

    integration_type = "pulse"

    def _client(self) -> httpx.AsyncClient:
        base_url = self.decrypted_config.get("base_url", _DEFAULT_BASE_URL)
        return httpx.AsyncClient(
            base_url=base_url,
            headers={"x-api-key": self.decrypted_config["api_key"]},
            timeout=_TIMEOUT,
        )

    # ── Poll ─────────────────────────────────────────────────────

    async def poll(self) -> ConnectorResult:
        """Fetch latest data for all mapped devices and Hub sensors."""
        result = ConnectorResult()

        async with self._client() as client:
            # 1. Poll Pulse devices (ambient) via bulk endpoint
            await self._poll_devices(client, result)

            # 2. Poll Hub sensors (bucket-level) individually
            await self._poll_hub_sensors(client, result)

        return result

    async def _poll_devices(self, client: httpx.AsyncClient, result: ConnectorResult) -> None:
        """Poll GET /all-devices for tent-mapped devices."""
        tent_maps = {dm.external_id: dm for dm in self.device_maps if dm.tent_id and not dm.bucket_id}
        if not tent_maps:
            return

        try:
            resp = await retry_request(
                lambda: client.get("/all-devices"),
                description="pulse.poll_devices",
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc, result)
            return
        except httpx.RequestError as exc:
            result.errors.append(f"Network error polling devices: {exc}")
            return

        data = resp.json()

        # /all-devices returns {deviceViewDtos: [...], ...}
        device_dtos = data.get("deviceViewDtos", [])
        for dto in device_dtos:
            device_id_str = str(dto.get("deviceId", ""))
            dm = tent_maps.get(device_id_str)
            if dm is None:
                continue

            reading = self._map_device_reading(dto, dm)
            if reading:
                result.readings.append(reading)

    async def _poll_hub_sensors(self, client: httpx.AsyncClient, result: ConnectorResult) -> None:
        """Poll GET /sensors/{id}/recent-data for bucket-mapped Hub sensors."""
        bucket_maps = {dm.external_id: dm for dm in self.device_maps if dm.bucket_id}
        if not bucket_maps:
            return

        for external_id, dm in bucket_maps.items():

            async def _get_recent(eid: str = external_id) -> httpx.Response:
                return await client.get(f"/sensors/{eid}/recent-data")

            try:
                resp = await retry_request(
                    lambda: _get_recent(),
                    description=f"pulse.poll_hub_sensor {external_id}",
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                self._handle_http_error(exc, result)
                continue
            except httpx.RequestError as exc:
                result.errors.append(f"Network error polling sensor {external_id}: {exc}")
                continue

            sensor_data = resp.json()
            reading = self._map_sensor_reading(sensor_data, dm)
            if reading:
                result.readings.append(reading)

    # ── Persistence ─────────────────────────────────────────────

    async def persist_readings(
        self,
        session: AsyncSession,
        result: ConnectorResult,
    ) -> int:
        """Write polled readings to TentSensorReading / BucketSensorReading."""
        return await write_pulse_readings(session, result.readings)

    # ── Webhook (not supported) ──────────────────────────────────

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Pulse does not support webhooks; return error."""
        result = ConnectorResult()
        result.errors.append("Pulse Grow does not support webhooks. Use polling instead.")
        return result

    # ── Discovery ────────────────────────────────────────────────

    async def discover_devices(self) -> list[DiscoveredDevice]:
        """Fetch all Pulse devices and Hub sensors for auto-discovery."""
        devices: list[DiscoveredDevice] = []

        async with self._client() as client:
            # Discover Pulse devices
            try:
                resp = await retry_request(
                    lambda: client.get("/all-devices"),
                    description="pulse.discover_all_devices",
                )
                resp.raise_for_status()
                data = resp.json()

                for dto in data.get("deviceViewDtos", []):
                    device_type_id = dto.get("deviceType", 0)
                    device_type = "pulse_pro" if device_type_id >= 2 else "pulse_one"
                    latest = {}
                    for pulse_key, tendril_key in _DEVICE_FIELD_MAP.items():
                        val = dto.get(pulse_key)
                        if val is not None:
                            latest[tendril_key] = val

                    devices.append(
                        DiscoveredDevice(
                            external_id=str(dto.get("deviceId", "")),
                            name=dto.get("name", f"Pulse Device {dto.get('deviceId', '')}"),
                            device_type=device_type,
                            latest_reading=latest or None,
                        )
                    )

                for hub_dto in data.get("hubViewDtos", []):
                    devices.append(
                        DiscoveredDevice(
                            external_id=f"hub_{hub_dto.get('id', '')}",
                            name=hub_dto.get("name", f"Pulse Hub {hub_dto.get('id', '')}"),
                            device_type="hub",
                            latest_reading=None,
                        )
                    )
            except httpx.HTTPStatusError as exc:
                logger.warning("Discovery failed: HTTP %s", exc.response.status_code)
                raise
            except httpx.RequestError as exc:
                logger.warning("Discovery failed: %s", exc)
                raise

            # Discover Hub sensors
            try:
                resp = await retry_request(
                    lambda: client.get("/sensors/ids"),
                    description="pulse.discover_sensor_ids",
                )
                resp.raise_for_status()
                sensor_ids = resp.json()

                for sid in sensor_ids:
                    sid_str = str(sid)

                    async def _get_details(s: str = sid_str) -> httpx.Response:
                        return await client.get(f"/sensors/{s}/details")

                    try:
                        detail_resp = await retry_request(
                            lambda: _get_details(),
                            description=f"pulse.discover_sensor_details {sid_str}",
                        )
                        detail_resp.raise_for_status()
                        details = detail_resp.json()
                        # details is a list with one item
                        detail = details[0] if isinstance(details, list) and details else {}
                        name = detail.get("name", f"Sensor {sid}")
                    except (httpx.HTTPStatusError, httpx.RequestError):
                        name = f"Sensor {sid}"

                    devices.append(
                        DiscoveredDevice(
                            external_id=str(sid),
                            name=name,
                            device_type="hub_sensor",
                            latest_reading=None,
                        )
                    )
            except (httpx.HTTPStatusError, httpx.RequestError):
                # Sensors API may not be available for all accounts
                pass

        return devices

    # ── Field mapping helpers ────────────────────────────────────

    def _map_device_reading(self, dto: dict[str, Any], dm: IntegrationDeviceMap) -> dict[str, Any] | None:
        """Map a Pulse device DTO to a TentSensorReading dict."""
        fields: dict[str, Any] = {}

        # Use sensor_mapping override if configured, otherwise default map
        mapping = dm.sensor_mapping if dm.sensor_mapping else _DEVICE_FIELD_MAP
        for pulse_key, tendril_key in mapping.items():
            val = dto.get(pulse_key)
            if val is not None:
                try:
                    fields[tendril_key] = float(val)
                except (ValueError, TypeError):
                    continue

        if not fields:
            return None

        return {
            "external_id": str(dto.get("deviceId", "")),
            "tent_id": str(dm.tent_id),
            "tenant_id": str(self.config.tenant_id),
            "target": "tent",
            **fields,
        }

    def _map_sensor_reading(self, sensor_data: dict[str, Any], dm: IntegrationDeviceMap) -> dict[str, Any] | None:
        """Map a Pulse Hub sensor reading to a BucketSensorReading dict."""
        fields: dict[str, Any] = {}

        # Hub sensor data has {sensorType, dataPointDto: {dataPointValues: [...]}}
        data_point = sensor_data.get("dataPointDto", {})
        values = data_point.get("dataPointValues", [])

        # Use sensor_mapping from the device map if configured
        mapping = dm.sensor_mapping if dm.sensor_mapping else {}

        for dpv in values:
            name = dpv.get("name", "").lower().replace(" ", "_")
            value = dpv.get("value")
            if value is None:
                continue

            # Try explicit mapping first, then fall back to _HUB_SENSOR_FIELD_MAP
            tendril_key = mapping.get(name) or _HUB_SENSOR_FIELD_MAP.get(name)
            if tendril_key:
                try:
                    fields[tendril_key] = float(value)
                except (ValueError, TypeError):
                    continue

        if not fields:
            return None

        return {
            "external_id": str(dm.external_id),
            "bucket_id": str(dm.bucket_id),
            "tenant_id": str(self.config.tenant_id),
            "target": "bucket",
            **fields,
        }

    def _handle_http_error(self, exc: httpx.HTTPStatusError, result: ConnectorResult) -> None:
        """Record an HTTP error in the result."""
        status = exc.response.status_code
        if status == 401:
            result.errors.append("Pulse API authentication failed — check your API key")
        elif status == 429:
            result.errors.append("Pulse API rate limit exceeded — reduce polling frequency")
        else:
            result.errors.append(f"Pulse API error: HTTP {status}")


# ---------------------------------------------------------------------------
# Utility: write readings to DB (called by scheduler / manual sync)
# ---------------------------------------------------------------------------


async def write_pulse_readings(
    session: AsyncSession,
    readings: list[dict[str, Any]],
) -> int:
    """Persist a list of mapped readings to the appropriate sensor tables.

    Returns the number of readings written.
    """
    count = 0
    now = datetime.now(UTC)

    for reading in readings:
        target = reading.pop("target", None)
        external_id = reading.pop("external_id", None)
        tenant_id = reading.pop("tenant_id", None)

        if target == "tent":
            tent_id = reading.pop("tent_id", None)
            if not tent_id or not tenant_id:
                continue
            row = TentSensorReading(
                tenant_id=tenant_id,
                tent_id=tent_id,
                device_id=f"pulse:{external_id}",
                recorded_at=now,
                **reading,
            )
            session.add(row)
            count += 1

        elif target == "bucket":
            bucket_id = reading.pop("bucket_id", None)
            if not bucket_id or not tenant_id:
                continue
            row = BucketSensorReading(
                tenant_id=tenant_id,
                bucket_id=bucket_id,
                device_id=f"pulse:{external_id}",
                recorded_at=now,
                **reading,
            )
            session.add(row)
            count += 1

            # RDWC: propagate header bucket readings to all site buckets
            count += await propagate_header_bucket_readings(session, bucket_id, row)

    return count
