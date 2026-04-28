"""Base connector class for integration polling and webhook handling."""

from __future__ import annotations

import abc
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.models import IntegrationConfig, IntegrationDeviceMap, IntegrationSyncLog


class ConnectorResult:
    """Result of a poll or webhook operation."""

    def __init__(self) -> None:
        self.readings: list[dict[str, Any]] = []
        self.errors: list[str] = []

    @property
    def readings_count(self) -> int:
        return len(self.readings)

    @property
    def status(self) -> str:
        if self.errors and not self.readings:
            return "error"
        if self.errors:
            return "partial"
        return "success"

    @property
    def error_message(self) -> str | None:
        return "; ".join(self.errors) if self.errors else None


class BaseConnector(abc.ABC):
    """Abstract base for all integration connectors.

    Each connector type (Pulse, Ecowitt, Home Assistant, etc.) subclasses
    this and implements ``poll`` and/or ``handle_webhook``.
    """

    integration_type: str = ""

    def __init__(
        self,
        config: IntegrationConfig,
        decrypted_config: dict[str, Any],
        device_maps: list[IntegrationDeviceMap],
    ) -> None:
        self.config = config
        self.decrypted_config = decrypted_config
        self.device_maps = device_maps

    @abc.abstractmethod
    async def poll(self) -> ConnectorResult:
        """Fetch latest data from the external API.

        Returns a ``ConnectorResult`` whose ``readings`` list contains dicts
        shaped like ``{"external_id": "...", "field": value, ...}``.
        """

    @abc.abstractmethod
    async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
        """Process an inbound webhook payload from the external platform."""

    async def persist_readings(
        self,
        session: AsyncSession,
        result: ConnectorResult,
    ) -> int:
        """Persist polled/webhook readings to sensor tables.

        Override in subclasses that produce readings.
        Returns the number of readings written.
        """
        return 0

    async def write_sync_log(
        self,
        session: AsyncSession,
        result: ConnectorResult,
    ) -> IntegrationSyncLog:
        """Persist a sync log entry for observability."""
        log = IntegrationSyncLog(
            tenant_id=self.config.tenant_id,
            integration_id=self.config.id,
            status=result.status,
            readings_count=result.readings_count,
            error_message=result.error_message,
        )
        session.add(log)
        return log


# ---- Connector registry ----

_registry: dict[str, type[BaseConnector]] = {}


def register_connector(connector_cls: type[BaseConnector]) -> type[BaseConnector]:
    """Decorator to register a connector class by its ``integration_type``."""
    _registry[connector_cls.integration_type] = connector_cls
    return connector_cls


def get_connector_class(integration_type: str) -> type[BaseConnector] | None:
    """Look up a registered connector class by type string."""
    return _registry.get(integration_type)
