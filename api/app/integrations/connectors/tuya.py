"""Tuya Smart Device connector.

Polls Tuya OpenAPI (Cloud Development) for device states — smart plugs,
temperature/humidity sensors, and switches.

Config schema (encrypted):
  {
    "access_id": "Tuya Cloud project Access ID",
    "access_secret": "Tuya Cloud project Access Secret",
    "region": "us"  (us, eu, cn, in)
  }

Device map external_id format: Tuya device_id (e.g., "bf3a0e...")
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

import httpx

from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector

TUYA_REGIONS = {
    "us": "https://openapi.tuyaus.com",
    "eu": "https://openapi.tuyaeu.com",
    "cn": "https://openapi.tuyacn.com",
    "in": "https://openapi.tuyain.com",
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
                device_id = dm.external_device_id
                try:
                    data = await self._api_get(client, f"/v1.0/devices/{device_id}/status")
                    if not data.get("success"):
                        result.errors.append(f"Tuya error for {device_id}: {data.get('msg')}")
                        continue

                    statuses = data.get("result", [])
                    reading: dict[str, Any] = {"external_id": device_id}

                    for status in statuses:
                        code = status.get("code", "")
                        value = status.get("value")

                        # Map common Tuya DPs to meaningful fields
                        if code == "switch_1" or code == "switch":
                            reading["is_on"] = bool(value)
                        elif code == "cur_power":
                            reading["power_w"] = value / 10 if isinstance(value, int | float) else None
                        elif code == "cur_current":
                            reading["current_ma"] = value
                        elif code == "cur_voltage":
                            reading["voltage_v"] = value / 10 if isinstance(value, int | float) else None
                        elif code in ("va_temperature", "temp_current"):
                            reading["temperature_c"] = value / 10 if isinstance(value, int | float) else None
                        elif code in ("va_humidity", "humidity_value"):
                            reading["humidity_pct"] = value
                        elif code == "add_ele":
                            reading["energy_kwh"] = value / 1000 if isinstance(value, int | float) else None

                    result.readings.append(reading)

                except httpx.RequestError as e:
                    result.errors.append(f"Connection error for {device_id}: {e!s}")
                except Exception as e:
                    result.errors.append(f"Tuya poll error for {device_id}: {e!s}")

        return result

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Handle Tuya cloud webhook push (device status change)."""
        result = ConnectorResult()

        # Tuya webhook payload structure: {"devId": "...", "status": [...]}
        device_id = payload.get("devId") or payload.get("device_id")
        if not device_id:
            result.errors.append("Missing devId in Tuya webhook payload")
            return result

        statuses = payload.get("status", [])
        reading: dict[str, Any] = {"external_id": device_id}

        for status in statuses:
            code = status.get("code", "")
            value = status.get("value")
            if code in ("switch_1", "switch"):
                reading["is_on"] = bool(value)
            elif code == "cur_power":
                reading["power_w"] = value / 10 if isinstance(value, int | float) else None
            elif code in ("va_temperature", "temp_current"):
                reading["temperature_c"] = value / 10 if isinstance(value, int | float) else None
            elif code in ("va_humidity", "humidity_value"):
                reading["humidity_pct"] = value

        result.readings.append(reading)
        return result

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
