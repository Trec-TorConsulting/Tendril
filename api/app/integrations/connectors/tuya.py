"""Tuya Smart Device connector.

Polls Tuya OpenAPI (Cloud Development) for device states — smart plugs,
temperature/humidity sensors, switches, and water quality monitors
(e.g., Ztech WiFi water monitors).

Config schema (encrypted):
  {
    "access_id": "Tuya Cloud project Access ID",
    "access_secret": "Tuya Cloud project Access Secret",
    "region": "us"  (us, eu, cn, in)
  }

Device map external_id format: Tuya device_id (e.g., "bf3a0e...")
"""

from __future__ import annotations

import contextlib
import hashlib
import hmac
import logging
import time
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import BucketSensorReading, TentSensorReading
from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tuya DP code → Tendril field mapping for water quality monitors
# ---------------------------------------------------------------------------

_WATER_DP_MAP: dict[str, str] = {
    # TDS / PPM
    "tds_in": "ppm",
    "tds_out": "ppm",
    "tds_value": "ppm",
    # pH
    "ph_value": "ph",
    "ph": "ph",
    # EC (μS/cm → mS/cm in persist)
    "ec_value": "ec",
    # Water temperature (Tuya sends deg C scaled x10)
    "water_temp": "water_temp_c",
    "temp_value": "water_temp_c",
    # Water level percentage
    "water_level": "water_level_pct",
    "level_percent": "water_level_pct",
    # Flow rate (L/min)
    "flow_rate": "flow_rate",
    "water_flow": "flow_rate",
    # Dissolved oxygen
    "dissolved_oxygen": "dissolved_oxygen",
}


# ---------------------------------------------------------------------------
# Discovery response
# ---------------------------------------------------------------------------


class DiscoveredDevice(BaseModel):
    external_id: str
    name: str
    device_type: str
    latest_reading: dict[str, Any] | None = None


TUYA_REGIONS = {
    "us": "https://openapi.tuyaus.com",
    "eu": "https://openapi.tuyaeu.com",
    "cn": "https://openapi.tuyacn.com",
    "in": "https://openapi.tuyain.com",
}

# Map Tuya device categories to human-readable types
_TUYA_CATEGORY_MAP: dict[str, str] = {
    "cz": "smart_plug",
    "kg": "switch",
    "dj": "light",
    "wsdcg": "temp_humidity_sensor",
    "sj": "water_monitor",
    "js": "water_monitor",
    "ylcg": "water_quality_sensor",
    "wk": "thermostat",
    "bh": "smart_plug",
}


@register_connector
class TuyaConnector(BaseConnector):
    integration_type = "tuya"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._access_token: str | None = None
        self._token_expiry: float = 0

    @property
    def base_url(self) -> str:
        region = self.decrypted_config.get("region", "us")
        return TUYA_REGIONS.get(region, TUYA_REGIONS["us"])

    @property
    def access_id(self) -> str:
        return self.decrypted_config["access_id"]

    @property
    def access_secret(self) -> str:
        return self.decrypted_config["access_secret"]

    def _sign(self, method: str, path: str, timestamp: str, token: str = "") -> str:
        """Generate Tuya API HMAC-SHA256 signature."""
        string_to_sign = f"{self.access_id}{token}{timestamp}{method}\n\n\n{path}"
        return (
            hmac.HMAC(
                self.access_secret.encode(),
                string_to_sign.encode(),
                hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        """Get or refresh Tuya access token."""
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        timestamp = str(int(time.time() * 1000))
        path = "/v1.0/token?grant_type=1"
        sign = self._sign("GET", path, timestamp)

        resp = await client.get(
            f"{self.base_url}{path}",
            headers={
                "client_id": self.access_id,
                "sign": sign,
                "t": timestamp,
                "sign_method": "HMAC-SHA256",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            raise ValueError(f"Tuya token error: {data.get('msg', 'unknown')}")

        result = data["result"]
        self._access_token = result["access_token"]
        self._token_expiry = time.time() + result.get("expire_time", 7200) - 60
        return self._access_token

    async def _api_get(self, client: httpx.AsyncClient, path: str) -> dict:
        """Make authenticated GET request to Tuya OpenAPI."""
        token = await self._get_token(client)
        timestamp = str(int(time.time() * 1000))
        sign = self._sign("GET", path, timestamp, token)

        resp = await client.get(
            f"{self.base_url}{path}",
            headers={
                "client_id": self.access_id,
                "access_token": token,
                "sign": sign,
                "t": timestamp,
                "sign_method": "HMAC-SHA256",
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def poll(self) -> ConnectorResult:
        """Fetch device status for all mapped Tuya devices."""
        result = ConnectorResult()

        if not self.device_maps:
            return result

        async with httpx.AsyncClient(timeout=15) as client:
            for dm in self.device_maps:
                device_id = dm.external_id
                try:
                    data = await self._api_get(client, f"/v1.0/devices/{device_id}/status")
                    if not data.get("success"):
                        result.errors.append(f"Tuya error for {device_id}: {data.get('msg')}")
                        continue

                    statuses = data.get("result", [])
                    reading = self._map_statuses(statuses, dm)
                    result.readings.append(reading)

                except httpx.RequestError as e:
                    result.errors.append(f"Connection error for {device_id}: {e!s}")
                except Exception as e:
                    result.errors.append(f"Tuya poll error for {device_id}: {e!s}")

        return result

    def _map_statuses(
        self,
        statuses: list[dict[str, Any]],
        dm: Any,
    ) -> dict[str, Any]:
        """Map Tuya status DP codes to Tendril fields.

        Handles power monitoring, ambient temp/humidity, and water quality DPs.
        """
        reading: dict[str, Any] = {
            "external_id": dm.external_id,
            "tenant_id": str(self.config.tenant_id),
        }

        # Attach target routing info from device map
        if dm.bucket_id:
            reading["target"] = "bucket"
            reading["bucket_id"] = str(dm.bucket_id)
        elif dm.tent_id:
            reading["target"] = "tent"
            reading["tent_id"] = str(dm.tent_id)

        # Use sensor_mapping override if configured
        custom_mapping = dm.sensor_mapping or {}

        for status in statuses:
            code = status.get("code", "")
            value = status.get("value")

            # Check custom sensor_mapping first
            if code in custom_mapping:
                tendril_key = custom_mapping[code]
                with contextlib.suppress(ValueError, TypeError):
                    reading[tendril_key] = float(value) if value is not None else None
                continue

            # Power monitoring DPs
            if code in ("switch_1", "switch"):
                reading["is_on"] = bool(value)
            elif code == "cur_power":
                reading["power_w"] = value / 10 if isinstance(value, int | float) else None
            elif code == "cur_current":
                reading["current_ma"] = value
            elif code == "cur_voltage":
                reading["voltage_v"] = value / 10 if isinstance(value, int | float) else None
            elif code == "add_ele":
                reading["energy_kwh"] = value / 1000 if isinstance(value, int | float) else None

            # Ambient temp / humidity
            elif code in ("va_temperature", "temp_current"):
                reading["temperature_c"] = value / 10 if isinstance(value, int | float) else None
            elif code in ("va_humidity", "humidity_value"):
                reading["humidity_pct"] = value

            # Water quality / flow DPs
            elif code in _WATER_DP_MAP:
                tendril_key = _WATER_DP_MAP[code]
                if value is None or not isinstance(value, int | float):
                    continue
                # Tuya water temp is deg C x 10
                if tendril_key == "water_temp_c":
                    reading[tendril_key] = value / 10
                # Tuya EC is μS/cm, store as mS/cm
                elif tendril_key == "ec":
                    reading[tendril_key] = value / 1000
                else:
                    reading[tendril_key] = float(value)

        return reading

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Handle Tuya cloud webhook push (device status change)."""
        result = ConnectorResult()

        # Tuya webhook payload structure: {"devId": "...", "status": [...]}
        device_id = payload.get("devId") or payload.get("device_id")
        if not device_id:
            result.errors.append("Missing devId in Tuya webhook payload")
            return result

        # Find matching device map
        dm = next((m for m in self.device_maps if m.external_id == device_id), None)
        if dm is None:
            result.errors.append(f"No device mapping for Tuya device {device_id}")
            return result

        statuses = payload.get("status", [])
        reading = self._map_statuses(statuses, dm)
        result.readings.append(reading)
        return result

    async def persist_readings(
        self,
        session: AsyncSession,
        result: ConnectorResult,
    ) -> int:
        """Write polled/webhook readings to BucketSensorReading or TentSensorReading."""
        count = 0
        now = datetime.now(UTC)

        for reading in result.readings:
            target = reading.get("target")
            external_id = reading.get("external_id")
            tenant_id = reading.get("tenant_id")

            if target == "bucket":
                bucket_id = reading.get("bucket_id")
                if not bucket_id or not tenant_id:
                    continue

                # Convert water_temp_c → water_temp_f for storage
                water_temp_c = reading.get("water_temp_c")
                water_temp_f = (water_temp_c * 9 / 5 + 32) if water_temp_c is not None else None

                row = BucketSensorReading(
                    tenant_id=tenant_id,
                    bucket_id=bucket_id,
                    device_id=f"tuya:{external_id}",
                    water_temp_f=water_temp_f,
                    ph=reading.get("ph"),
                    ec=reading.get("ec"),
                    ppm=reading.get("ppm"),
                    water_level_pct=reading.get("water_level_pct"),
                    flow_rate=reading.get("flow_rate"),
                    dissolved_oxygen=reading.get("dissolved_oxygen"),
                    recorded_at=now,
                )
                session.add(row)
                count += 1

            elif target == "tent":
                tent_id = reading.get("tent_id")
                if not tent_id or not tenant_id:
                    continue

                # Convert temperature_c → ambient_temp_f for storage
                temp_c = reading.get("temperature_c")
                ambient_temp_f = (temp_c * 9 / 5 + 32) if temp_c is not None else None

                row = TentSensorReading(
                    tenant_id=tenant_id,
                    tent_id=tent_id,
                    device_id=f"tuya:{external_id}",
                    ambient_temp_f=ambient_temp_f,
                    ambient_humidity=reading.get("humidity_pct"),
                    recorded_at=now,
                )
                session.add(row)
                count += 1

        return count

    # ── Discovery ────────────────────────────────────────────────

    async def discover_devices(self) -> list[DiscoveredDevice]:
        """Discover all Tuya devices linked to the cloud project.

        Tries multiple API endpoints since the correct one depends on
        the Tuya Cloud project type (Smart Home vs Industry).
        """
        devices: list[DiscoveredDevice] = []

        async with httpx.AsyncClient(timeout=15) as client:
            # Strategy 1: Get linked app user's devices (Smart Home projects)
            uid = self.decrypted_config.get("uid")
            if not uid:
                uid = await self._get_app_user_uid(client)

            if uid:
                data = await self._api_get(client, f"/v1.0/users/{uid}/devices")
                if data.get("success"):
                    for dev in data.get("result", []):
                        devices.append(self._device_to_discovered(dev))
                    if devices:
                        return devices

            # Strategy 2: Direct device list (Industry / custom projects)
            try:
                data = await self._api_get(client, "/v1.0/devices")
                if data.get("success"):
                    result = data.get("result", {})
                    dev_list = result.get("list", []) if isinstance(result, dict) else result
                    for dev in dev_list:
                        devices.append(self._device_to_discovered(dev))
                    if devices:
                        return devices
            except Exception as exc:
                logger.debug("Tuya /v1.0/devices fallback failed: %s", exc)

            # Strategy 3: IoT Core endpoint
            try:
                data = await self._api_get(client, "/v2.0/cloud/thing/device?page_no=1&page_size=50")
                if data.get("success"):
                    for dev in data.get("result", {}).get("list", []):
                        devices.append(self._device_to_discovered(dev))
            except Exception as exc:
                if not devices:
                    logger.warning("Tuya discovery failed all endpoints: %s", exc)
                    raise

        return devices

    async def _get_app_user_uid(self, client: httpx.AsyncClient) -> str | None:
        """Get the UID of the linked Tuya app user."""
        try:
            data = await self._api_get(client, "/v1.0/token?grant_type=1")
            # UID is returned with the token; check cached token response
            # Try the users endpoint instead
            data = await self._api_get(client, "/v1.0/apps/users?page_no=1&page_size=1")
            if data.get("success"):
                users = data.get("result", {}).get("list", [])
                if users:
                    return users[0].get("uid")
        except Exception as exc:
            logger.debug("Failed to fetch Tuya app user UID: %s", exc)
        return None

    def _device_to_discovered(self, dev: dict[str, Any]) -> DiscoveredDevice:
        """Convert a Tuya API device dict to a DiscoveredDevice."""
        category = dev.get("category", "")
        device_type = _TUYA_CATEGORY_MAP.get(category, category or "unknown")
        return DiscoveredDevice(
            external_id=dev.get("id", ""),
            name=dev.get("name", dev.get("id", "Unknown")),
            device_type=device_type,
        )

    # ── Device Control ───────────────────────────────────────────

    async def toggle_device(self, device_id: str, on: bool) -> dict:
        """Turn a Tuya device on or off. Used by Tendril automation."""
        async with httpx.AsyncClient(timeout=10) as client:
            token = await self._get_token(client)
            timestamp = str(int(time.time() * 1000))
            path = f"/v1.0/devices/{device_id}/commands"
            sign = self._sign("POST", path, timestamp, token)

            resp = await client.post(
                f"{self.base_url}{path}",
                headers={
                    "client_id": self.access_id,
                    "access_token": token,
                    "sign": sign,
                    "t": timestamp,
                    "sign_method": "HMAC-SHA256",
                    "Content-Type": "application/json",
                },
                json={"commands": [{"code": "switch_1", "value": on}]},
            )
            resp.raise_for_status()
            return resp.json()
