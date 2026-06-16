"""OpenSprinkler connector.

Polls OpenSprinkler local REST API for station/zone status, program data,
and rain sensor readings. Can trigger zone runs.

Config schema (encrypted):
  {
    "base_url": "http://192.168.x.x:8080",
    "password_hash": "md5-hash-of-device-password"
  }

Device map external_id format: "station_0", "station_1", etc. (0-indexed zone)
"""

from __future__ import annotations

import hashlib
from typing import Any

import httpx

from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector
from app.integrations.connectors.retry import retry_request


@register_connector
class OpenSprinklerConnector(BaseConnector):
    integration_type = "opensprinkler"

    @property
    def base_url(self) -> str:
        return self.decrypted_config["base_url"].rstrip("/")

    @property
    def password_hash(self) -> str:
        # OpenSprinkler uses MD5 hash of the device password in API calls
        pw = self.decrypted_config.get("password_hash", "")
        if pw and len(pw) == 32:
            return pw
        # If raw password provided, hash it (OpenSprinkler API requires MD5)
        return hashlib.md5(pw.encode(), usedforsecurity=False).hexdigest()

    async def _get(self, endpoint: str) -> dict:
        """Make GET request to OpenSprinkler API."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await retry_request(
                lambda: client.get(
                    f"{self.base_url}/{endpoint}",
                    params={"pw": self.password_hash},
                ),
                description=f"opensprinkler.get {endpoint}",
            )
            resp.raise_for_status()
            return resp.json()

    async def poll(self) -> ConnectorResult:
        """Fetch controller status, station states, and sensor data."""
        result = ConnectorResult()

        try:
            # Get all controller variables and station status in one call
            data = await self._get("ja")  # "ja" = get all (json all)

            settings = data.get("settings", {})
            stations = data.get("stations", {})
            status = data.get("status", {})

            # Rain sensor
            rain_delay = settings.get("rd", 0)  # rain delay in hours
            rain_sensor = settings.get("rs", 0)  # rain sensor active (1=raining)

            result.readings.append(
                {
                    "external_id": "rain_sensor",
                    "rain_active": bool(rain_sensor),
                    "rain_delay_hours": rain_delay,
                    "device_type": "sensor",
                }
            )

            # Station/zone statuses
            sn_list = status.get("sn", [])  # station status array (1=on, 0=off)
            ps_list = data.get("settings", {}).get("ps", [])  # program status per station
            station_names = stations.get("snames", [])

            for i, is_on in enumerate(sn_list):
                name = station_names[i] if i < len(station_names) else f"Station {i + 1}"
                remaining = 0
                if ps_list and i < len(ps_list) and isinstance(ps_list[i], list) and len(ps_list[i]) >= 2:
                    remaining = ps_list[i][1]
                result.readings.append(
                    {
                        "external_id": f"station_{i}",
                        "name": name,
                        "is_running": bool(is_on),
                        "remaining_seconds": remaining,
                        "device_type": "zone",
                    }
                )

            # Flow sensor (if equipped)
            flow = settings.get("flcrt", 0)  # flow count current
            if flow:
                result.readings.append(
                    {
                        "external_id": "flow_sensor",
                        "flow_count": flow,
                        "device_type": "sensor",
                    }
                )

        except httpx.RequestError as e:
            result.errors.append(f"Connection error: {e!s}")
        except Exception as e:
            result.errors.append(f"OpenSprinkler poll error: {e!s}")

        return result

    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """OpenSprinkler doesn't push webhooks — use polling only."""
        result = ConnectorResult()
        result.errors.append("OpenSprinkler does not support webhooks — use polling")
        return result

    async def run_station(self, station_index: int, duration_seconds: int) -> dict:
        """Manually trigger a station/zone run.

        Used by Tendril automation to water plants based on AI recommendations.
        """
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await retry_request(
                lambda: client.get(
                    f"{self.base_url}/cm",
                    params={
                        "pw": self.password_hash,
                        "sid": station_index,
                        "en": 1,
                        "t": duration_seconds,
                    },
                ),
                description=f"opensprinkler.run_station sid={station_index}",
            )
            resp.raise_for_status()
            return resp.json()

    async def stop_station(self, station_index: int) -> dict:
        """Stop a running station."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await retry_request(
                lambda: client.get(
                    f"{self.base_url}/cm",
                    params={
                        "pw": self.password_hash,
                        "sid": station_index,
                        "en": 0,
                        "t": 0,
                    },
                ),
                description=f"opensprinkler.stop_station sid={station_index}",
            )
            resp.raise_for_status()
            return resp.json()

    async def get_programs(self) -> list[dict]:
        """List all irrigation programs (for display in Tendril UI)."""
        data = await self._get("jp")  # json programs
        programs = data.get("pd", [])
        return [
            {
                "index": i,
                "enabled": bool(p[0] & 0x01) if p else False,
                "name": p[5] if len(p) > 5 else f"Program {i + 1}",
            }
            for i, p in enumerate(programs)
        ]
