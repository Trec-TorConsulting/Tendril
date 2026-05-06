"""Home Assistant Bridge connector.

Polls HA REST API for entity states and maps them to Tendril sensor readings.
Can also call HA services for automation (e.g., toggle fans/pumps).

Config schema (encrypted):
  {
    "base_url": "http://192.168.x.x:8123",
    "token": "long-lived-access-token"
  }

Device map external_id format: "sensor.tent_temperature" (HA entity_id)
"""

from __future__ import annotations

from typing import Any

import httpx

from app.integrations.connectors.base import BaseConnector, ConnectorResult, register_connector


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
                entity_id = dm.external_device_id
                try:
                    resp = await client.get(
                        f"{self.base_url}/api/states/{entity_id}",
                        headers=self.headers,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        state = data.get("state")
                        attrs = data.get("attributes", {})

                        # Try to parse numeric state
                        try:
                            numeric_value = float(state)
                        except (ValueError, TypeError):
                            numeric_value = None

                        reading = {
                            "external_id": entity_id,
                            "state": state,
                            "value": numeric_value,
                            "unit": attrs.get("unit_of_measurement"),
                            "device_class": attrs.get("device_class"),
                            "friendly_name": attrs.get("friendly_name"),
                            "last_updated": data.get("last_updated"),
                        }
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

        # Expect payload: {"entity_id": "...", "state": "...", "attributes": {...}}
        entity_id = payload.get("entity_id")
        state = payload.get("state")
        if not entity_id:
            result.errors.append("Missing entity_id in webhook payload")
            return result

        try:
            numeric_value = float(state) if state else None
        except (ValueError, TypeError):
            numeric_value = None

        attrs = payload.get("attributes", {})
        result.readings.append(
            {
                "external_id": entity_id,
                "state": state,
                "value": numeric_value,
                "unit": attrs.get("unit_of_measurement"),
                "device_class": attrs.get("device_class"),
                "friendly_name": attrs.get("friendly_name"),
            }
        )

        return result

    async def call_service(self, domain: str, service: str, data: dict[str, Any] | None = None) -> dict:
        """Call a Home Assistant service (e.g., switch.turn_on).

        Used by Tendril automation rules to control devices via HA.
        """
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.base_url}/api/services/{domain}/{service}",
                headers=self.headers,
                json=data or {},
            )
            resp.raise_for_status()
            return resp.json()

    async def list_entities(self, domain_filter: str | None = None) -> list[dict]:
        """List all HA entities (for discovery UI). Optionally filter by domain."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{self.base_url}/api/states", headers=self.headers)
            resp.raise_for_status()
            entities = resp.json()

        if domain_filter:
            entities = [e for e in entities if e.get("entity_id", "").startswith(f"{domain_filter}.")]

        return [
            {
                "entity_id": e["entity_id"],
                "state": e["state"],
                "friendly_name": e.get("attributes", {}).get("friendly_name"),
                "device_class": e.get("attributes", {}).get("device_class"),
                "unit": e.get("attributes", {}).get("unit_of_measurement"),
            }
            for e in entities
        ]
