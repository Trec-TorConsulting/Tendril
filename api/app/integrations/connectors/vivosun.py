"""VIVOSUN GrowHub connector — polls the Vivosun cloud API for environment data.

Supports GrowHub E42A/E42A+ controllers, AeroStream H19 humidifiers,
and AeroFlux W70 heaters. Maps ambient readings (inside/outside temp,
humidity, VPD) to TentSensorReading.

Uses the Vivosun cloud REST API (api-prod.next.vivosun.com) to authenticate
with email/password and poll historical sensor data via the PointLog endpoint.
"""

from __future__ import annotations

import hashlib
import json as json_mod
import logging
import secrets
import string
import time
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import TentSensorReading
from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector
from app.integrations.models import IntegrationDeviceMap

logger = logging.getLogger("tendril.integrations.vivosun")

_TIMEOUT = 30.0
_BASE_URL = "https://api-prod.next.vivosun.com"

# Must match current Play Store release or the API rejects requests.
_APP_VERSION = "4.63.1"
_API_PROTOCOL_VERSION = "1.0.5"
_SERVER_PLATFORM = "android"
_SP_APP_ID = "com.vivosun.android"

_BASE_HEADERS: dict[str, str] = {
    "Server-Platform": _SERVER_PLATFORM,
    "Api-Version": _API_PROTOCOL_VERSION,
    "App-Version": _APP_VERSION,
}

# ── POST body encryption ────────────────────────────────────────────────
# The Vivosun cloud rejects unencrypted production POST requests (except login)
# with a misleading "Your app version is outdated" (code 60001). This mirrors
# the official Android app's VSHttpHeaderInterceptor encryption scheme.
_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits
_AES_KEY_LENGTHS = (16, 24, 32)
_IV_LENGTH = 16
_MD5_HEX_LENGTH = 32


def _encrypt_request_body(plaintext: bytes, *, timestamp_ms: int) -> tuple[str, str, bytes]:
    """Encrypt a POST body, returning (request_time, request_code, encrypted_body)."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.padding import PKCS7

    md5_hex = hashlib.md5(str(timestamp_ms).encode(), usedforsecurity=False).hexdigest()

    key_len = secrets.choice(_AES_KEY_LENGTHS)
    key_start = secrets.randbelow(_MD5_HEX_LENGTH - key_len + 1)
    key_end = key_start + key_len
    aes_key = md5_hex[key_start:key_end].encode()

    salt_len = _IV_LENGTH + secrets.randbelow(84)  # 16..99, matches app
    salt = "".join(secrets.choice(_ALPHABET) for _ in range(salt_len))
    iv_start = secrets.randbelow(salt_len - _IV_LENGTH + 1)
    iv_end = iv_start + _IV_LENGTH
    aes_iv = salt[iv_start:iv_end].encode()

    padder = PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(plaintext) + padder.finalize()
    encryptor = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv)).encryptor()
    content_hex = (encryptor.update(padded) + encryptor.finalize()).hex()

    request_code = f"AC5-{key_start}-{key_end}-{iv_start}-{iv_end}-{salt}"
    body = json_mod.dumps({"content": content_hex}, separators=(",", ":")).encode()
    return str(timestamp_ms), request_code, body


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
        """Return auth headers for authenticated endpoints."""
        return {
            **_BASE_HEADERS,
            "login-token": self._login_token,
            "access-token": self._access_token,
        }

    @property
    def _login_token(self) -> str:
        return self.decrypted_config.get("login_token", "")

    @property
    def _access_token(self) -> str:
        return self.decrypted_config.get("access_token", "")

    async def _authenticate(self, client: httpx.AsyncClient) -> bool:
        """Authenticate with email/password, store tokens in decrypted_config."""
        email = self.decrypted_config.get("email", "")
        password = self.decrypted_config.get("password", "")
        if not email or not password:
            logger.warning("Vivosun login skipped: missing email or password in config")
            return False

        login_body = json_mod.dumps(
            {
                "email": email,
                "password": password,
                "spAppId": _SP_APP_ID,
                "spClientId": str(uuid4()),
                "spSessionId": str(uuid4()),
            },
            separators=(",", ":"),
        ).encode()

        try:
            resp = await client.post(
                f"{_BASE_URL}/user/login",
                headers={**_BASE_HEADERS, "Content-Type": "application/json"},
                content=login_body,
            )
            resp.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning(
                "Vivosun login HTTP error: %s (status=%s)",
                exc,
                getattr(getattr(exc, "response", None), "status_code", "?"),
            )
            return False

        data = resp.json()
        if not data.get("success", True):
            logger.warning(
                "Vivosun login rejected: %s (code=%s)", data.get("message", "unknown"), data.get("code", "?")
            )
            return False
        result_data = data.get("data", data)
        self.decrypted_config["login_token"] = result_data.get("loginToken", "")
        self.decrypted_config["access_token"] = result_data.get("accessToken", "")
        if not self._login_token or not self._access_token:
            logger.warning("Vivosun login response missing tokens: keys=%s", list(result_data.keys()))
            return False
        return True

    async def _ensure_auth(self, client: httpx.AsyncClient) -> bool:
        """Ensure we have valid tokens, re-authenticating if needed.

        Always re-authenticate fresh — tokens from previous protocol versions
        may be stored but invalid.
        """
        if self._login_token and self._access_token:
            # Validate tokens with a lightweight request
            try:
                resp = await client.get(
                    f"{_BASE_URL}/iot/device/getTotalList",
                    headers=self._headers(),
                )
                if resp.status_code != 401:
                    return True
            except httpx.RequestError:
                pass
            # Tokens are stale, clear and re-authenticate
            self.decrypted_config.pop("login_token", None)
            self.decrypted_config.pop("access_token", None)
        return await self._authenticate(client)

    async def _encrypted_post(self, client: httpx.AsyncClient, path: str, payload: dict[str, Any]) -> httpx.Response:
        """Send an encrypted POST request (required for all non-login POSTs)."""
        plaintext = json_mod.dumps(payload, separators=(",", ":")).encode()
        timestamp_ms = int(time.time() * 1000)
        request_time, request_code, body = _encrypt_request_body(plaintext, timestamp_ms=timestamp_ms)

        headers = {
            **self._headers(),
            "Content-Type": "application/json",
            "Request-Time": request_time,
            "Request-Code": request_code,
        }
        return await client.post(f"{_BASE_URL}{path}", headers=headers, content=body)

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
        and a recent time window. Times are epoch milliseconds.
        """
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - (15 * 60 * 1000)  # 15 minutes ago

        payload: dict[str, Any] = {
            "deviceId": external_id,
            "startTime": start_ms,
            "endTime": now_ms,
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
            resp = await self._encrypted_post(client, "/iot/data/getPointLog", payload)
            if resp.status_code == 401:
                # Clear stale tokens and try re-authenticating once
                self.decrypted_config.pop("login_token", None)
                self.decrypted_config.pop("access_token", None)
                if await self._authenticate(client):
                    resp = await self._encrypted_post(client, "/iot/data/getPointLog", payload)
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
