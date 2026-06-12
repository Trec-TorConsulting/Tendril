"""VIVOSUN GrowHub connector — polls the Vivosun cloud API for environment data.

Supports GrowHub E42A/E42A+ controllers, AeroStream H19 humidifiers,
and AeroFlux W70 heaters. Maps ambient readings (inside/outside temp,
humidity, VPD) to TentSensorReading.

Uses the Vivosun cloud REST API (api-prod.next.vivosun.com) to authenticate
with email/password and poll historical sensor data via the PointLog endpoint.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import TentSensorReading
from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector
from app.integrations.models import IntegrationDeviceMap

logger = logging.getLogger("tendril.integrations.vivosun")

_TIMEOUT = 30.0
_BASE_URL = "https://api-prod.next.vivosun.com"
# App version headers required by the Vivosun cloud API.
# Without these the API returns "Your app version is outdated" errors.
_APP_VERSION = "3.3.0"
_APP_HEADERS: dict[str, str] = {
    "appVersion": _APP_VERSION,
    "platform": "android",
    "User-Agent": f"GrowHub/{_APP_VERSION} (Android)",
}

# Vivosun GrowHub E42A/E42A+ PointLog fields → TentSensorReading columns
# All temp/humidity/VPD values are raw integers divided by 100.
# Field names from the actual API response: bTemp (built-in), pTemp (probe)
# The probe sensor goes INSIDE the tent; the built-in is on the controller body OUTSIDE.
_GROWHUB_FIELD_MAP: dict[str, str] = {
    "pTemp": "ambient_temp_f",  # Probe sensor temp INSIDE tent (°C → °F)
    "pHumi": "ambient_humidity",  # Probe sensor humidity INSIDE tent
    "pVpd": "vpd",  # Probe sensor VPD INSIDE tent
}

# Sentinel value from Vivosun API indicating sensor unavailable
_SENTINEL = -6666


# ---------------------------------------------------------------------------
# Config schema
# ---------------------------------------------------------------------------


class VivosunConfig(BaseModel):
    """Validated config shape for VIVOSUN integrations."""

    email: str = Field(..., min_length=1, description="Vivosun account email")
    password: str = Field(..., min_length=1, description="Vivosun account password")


# ---------------------------------------------------------------------------
# Discovery response
# ---------------------------------------------------------------------------


class DiscoveredDevice(BaseModel):
    external_id: str
    name: str
    device_type: str  # "growhub", "humidifier", "heater"
    latest_reading: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


@register_connector
class VivosunConnector(BaseConnector):
    """Connector for VIVOSUN GrowHub cloud API (polling mode only)."""

    integration_type = "vivosun"

    def _headers(self) -> dict[str, str]:
        """Return auth headers using stored tokens."""
        return {
            **_APP_HEADERS,
            "login-token": self._login_token,
            "access-token": self._access_token,
            "Content-Type": "application/json",
        }

    @property
    def _login_token(self) -> str:
        return self.decrypted_config.get("login_token", "")

    @property
    def _access_token(self) -> str:
        return self.decrypted_config.get("access_token", "")

    async def _authenticate(self, client: httpx.AsyncClient) -> bool:
        """Authenticate with email/password, store tokens in decrypted_config.

        The Vivosun cloud API (v3.3+) requires the password as an MD5 hash
        and additional fields in the login body.
        """
        email = self.decrypted_config.get("email", "")
        password = self.decrypted_config.get("password", "")
        if not email or not password:
            return False

        # Vivosun API expects MD5-hashed password
        password_md5 = hashlib.md5(password.encode()).hexdigest()  # noqa: S324

        try:
            resp = await client.post(
                f"{_BASE_URL}/user/login",
                headers={**_APP_HEADERS, "Content-Type": "application/json"},
                json={
                    "email": email,
                    "password": password_md5,
                    "appVersion": _APP_VERSION,
                    "clientType": "android",
                },
            )
            if resp.status_code == 401 or (resp.status_code == 200 and not resp.json().get("success", True)):
                # Retry with raw password for accounts that haven't migrated
                resp = await client.post(
                    f"{_BASE_URL}/user/login",
                    headers={**_APP_HEADERS, "Content-Type": "application/json"},
                    json={
                        "email": email,
                        "password": password,
                        "appVersion": _APP_VERSION,
                        "clientType": "android",
                    },
                )
            resp.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("Vivosun login failed: %s", exc)
            return False

        data = resp.json()
        if not data.get("success", True):
            logger.warning("Vivosun login rejected: %s", data.get("message", "unknown"))
            return False
        result_data = data.get("data", data)
        self.decrypted_config["login_token"] = result_data.get("loginToken", "")
        self.decrypted_config["access_token"] = result_data.get("accessToken", "")
        return bool(self._login_token and self._access_token)

    async def _ensure_auth(self, client: httpx.AsyncClient) -> bool:
        """Ensure we have valid tokens, re-authenticating if needed."""
        if self._login_token and self._access_token:
            return True
        return await self._authenticate(client)

    # ── Poll ─────────────────────────────────────────────────────

    async def poll(self) -> ConnectorResult:
        """Fetch latest sensor data for all mapped devices."""
        result = ConnectorResult()

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            if not await self._ensure_auth(client):
                result.errors.append("Vivosun authentication failed — check email/password")
                return result

            tent_maps = {dm.external_id: dm for dm in self.device_maps if dm.tent_id}
            if not tent_maps:
                result.errors.append("No device maps configured — map devices to tents first")
                return result

            # Fetch device list to get scene_id for each device
            scene_map = await self._fetch_scene_map(client)

            for external_id, dm in tent_maps.items():
                # Get scene_id from device map metadata first, fall back to API
                scene_id: int | None = None
                if dm.sensor_mapping and "scene_id" in dm.sensor_mapping:
                    scene_id = int(dm.sensor_mapping["scene_id"])
                elif external_id in scene_map:
                    scene_id = scene_map[external_id]

                await self._poll_device(client, external_id, dm, result, scene_id=scene_id)

        return result

    async def _fetch_scene_map(self, client: httpx.AsyncClient) -> dict[str, int]:
        """Fetch device list to build device_id -> scene_id mapping."""
        try:
            resp = await client.get(
                f"{_BASE_URL}/iot/device/getTotalList",
                headers=self._headers(),
            )
            resp.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("Failed to fetch device list for scene mapping: %s", exc)
            return {}

        data = resp.json()
        raw = data.get("data", data)
        scene_map: dict[str, int] = {}
        if isinstance(raw, dict):
            device_group = raw.get("deviceGroup")
            if isinstance(device_group, dict):
                for _category, group_devices in device_group.items():
                    if isinstance(group_devices, list):
                        for device in group_devices:
                            did = str(device.get("deviceId", ""))
                            scene = device.get("scene", {})
                            sid = scene.get("sceneId") if isinstance(scene, dict) else None
                            if did and sid is not None:
                                scene_map[did] = int(sid)
        return scene_map

    def _build_pointlog_payload(self, external_id: str, scene_id: int | None) -> dict[str, Any]:
        """Build the correct getPointLog payload.

        Requires sceneId + deviceId, reportType=0, timeLevel=ONE_MINUTE,
        and a recent time window.
        """
        now = datetime.now(UTC)
        start = now - timedelta(minutes=15)

        payload: dict[str, Any] = {
            "deviceId": external_id,
            "startTime": start.strftime("%Y-%m-%d %H:%M:%S"),
            "endTime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "reportType": 0,
            "orderBy": "asc",
            "timeLevel": "ONE_MINUTE",
        }
        if scene_id:
            payload["sceneId"] = scene_id
        return payload

    async def _poll_device(
        self,
        client: httpx.AsyncClient,
        external_id: str,
        dm: IntegrationDeviceMap,
        result: ConnectorResult,
        *,
        scene_id: int | None = None,
    ) -> None:
        """Poll sensor data for a single device via PointLog API."""
        payload = self._build_pointlog_payload(external_id, scene_id)

        try:
            resp = await client.post(
                f"{_BASE_URL}/iot/data/getPointLog",
                headers=self._headers(),
                json=payload,
            )
            if resp.status_code == 401:
                # Clear stale tokens and try re-authenticating once
                self.decrypted_config.pop("login_token", None)
                self.decrypted_config.pop("access_token", None)
                if await self._authenticate(client):
                    resp = await client.post(
                        f"{_BASE_URL}/iot/data/getPointLog",
                        headers=self._headers(),
                        json=payload,
                    )
                    resp.raise_for_status()
                else:
                    result.errors.append("Vivosun re-authentication failed")
                    return
            else:
                resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc, result)
            return
        except httpx.RequestError as exc:
            result.errors.append(f"Network error polling device {external_id}: {exc}")
            return

        data = resp.json()
        if not isinstance(data, dict) or not data.get("success"):
            msg = data.get("message", "unknown error") if isinstance(data, dict) else "invalid response"
            result.errors.append(f"Vivosun API error for {external_id}: {msg}")
            return

        # Response: data.data.iotDataLogList[]
        inner = data.get("data", {})
        entries = inner.get("iotDataLogList", []) if isinstance(inner, dict) else []
        if not entries:
            return

        latest = entries[-1]
        reading = self._map_reading(latest, dm, external_id)
        if reading:
            result.readings.append(reading)

    # ── Persistence ─────────────────────────────────────────────

    async def persist_readings(
        self,
        session: AsyncSession,
        result: ConnectorResult,
    ) -> int:
        """Write polled readings to TentSensorReading."""
        count = 0
        now = datetime.now(UTC)

        for reading in result.readings:
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
                    device_id=f"vivosun:{external_id}",
                    recorded_at=now,
                    **reading,
                )
                session.add(row)
                count += 1

        return count

    # ── Webhook (not supported) ──────────────────────────────────

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Vivosun does not support webhooks; return error."""
        result = ConnectorResult()
        result.errors.append("VIVOSUN does not support webhooks. Use polling instead.")
        return result

    # ── Discovery ────────────────────────────────────────────────

    async def discover_devices(self) -> list[DiscoveredDevice]:
        """List all Vivosun devices on the account."""
        devices: list[DiscoveredDevice] = []

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            if not await self._ensure_auth(client):
                raise RuntimeError("Vivosun authentication failed — check email/password")

            try:
                resp = await client.get(
                    f"{_BASE_URL}/iot/device/getTotalList",
                    headers=self._headers(),
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.warning("Vivosun discovery failed: HTTP %s", exc.response.status_code)
                raise
            except httpx.RequestError as exc:
                logger.warning("Vivosun discovery failed: %s", exc)
                raise

            data = resp.json()
            raw = data.get("data", data)

            # Vivosun API returns devices nested under deviceGroup categories
            # e.g. {"deviceGroup": {"GROW": [...], "HUMIDIFIER": [...]}}
            device_list: list[dict[str, Any]] = []
            if isinstance(raw, dict):
                device_group = raw.get("deviceGroup")
                if isinstance(device_group, dict):
                    for _category, group_devices in device_group.items():
                        if isinstance(group_devices, list):
                            device_list.extend(group_devices)
                else:
                    # Fallback for flat list responses
                    device_list = raw.get("list", raw.get("devices", []))
            elif isinstance(raw, list):
                device_list = raw

            for device in device_list:
                device_id = str(device.get("deviceId", device.get("id", "")))
                name = device.get("name", device.get("deviceName", f"Vivosun {device_id}"))
                # Use clientId prefix to determine model (e.g. "vivosun-VSCTLE42AP-...")
                client_id = device.get("clientId", "").lower()
                model = device.get("model", device.get("deviceType", "")).lower()

                # Classify device type from model string or clientId
                if "e42" in model or "e42" in client_id or "growhub" in model or "controller" in name.lower():
                    device_type = "growhub"
                elif "h19" in model or "humidifier" in model or "aerostream" in model:
                    device_type = "humidifier"
                elif "w70" in model or "heater" in model or "aeroflux" in model:
                    device_type = "heater"
                elif "cam" in model or "c4" in model:
                    device_type = "camera"
                else:
                    device_type = "unknown"

                devices.append(
                    DiscoveredDevice(
                        external_id=device_id,
                        name=name,
                        device_type=device_type,
                        latest_reading=None,
                    )
                )

        return devices

    # ── Field mapping helpers ────────────────────────────────────

    def _map_reading(self, entry: dict[str, Any], dm: IntegrationDeviceMap, external_id: str) -> dict[str, Any] | None:
        """Map a Vivosun PointLog entry to a TentSensorReading dict.

        Vivosun values are raw integers / 100 in °C. We convert to °F for
        temperature fields to match Tendril's convention.
        """
        fields: dict[str, Any] = {}

        # Always use the default field map for GrowHub devices
        mapping = _GROWHUB_FIELD_MAP

        for vivosun_key, tendril_key in mapping.items():
            val = entry.get(vivosun_key)
            if val is None or val == _SENTINEL:
                continue

            try:
                numeric_val = float(val) / 100.0
            except (ValueError, TypeError):
                continue

            # Convert °C → °F for temperature fields
            if "temp" in tendril_key.lower() and "_f" in tendril_key:
                numeric_val = numeric_val * 9.0 / 5.0 + 32.0

            fields[tendril_key] = round(numeric_val, 2)

        if not fields:
            return None

        return {
            "external_id": external_id,
            "tent_id": str(dm.tent_id),
            "tenant_id": str(self.config.tenant_id),
            "target": "tent",
            **fields,
        }

    def _handle_http_error(self, exc: httpx.HTTPStatusError, result: ConnectorResult) -> None:
        """Record an HTTP error in the result."""
        status = exc.response.status_code
        if status == 401:
            result.errors.append("Vivosun API authentication failed — check email/password")
        elif status == 429:
            result.errors.append("Vivosun API rate limit exceeded — reduce polling frequency")
        else:
            result.errors.append(f"Vivosun API error: HTTP {status}")
