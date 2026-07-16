"""Base connector class for integration polling and webhook handling."""

from __future__ import annotations

import abc
import uuid
from functools import lru_cache
from typing import Any

from sqlalchemy import select
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

    @staticmethod
    def _sanitize_readings(readings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Strip internal IDs from readings for human-readable sync log storage."""
        skip_keys = {"tenant_id", "bucket_id", "tent_id"}
        sanitized = []
        for r in readings:
            sanitized.append({k: v for k, v in r.items() if k not in skip_keys and v is not None})
        return sanitized or None  # type: ignore[return-value]

    async def propagate_header_readings(
        self,
        session: AsyncSession,
        header_bucket_id: str,
        reading_row: Any,
    ) -> int:
        """For RDWC header buckets, duplicate the reading to all site buckets
        in the same grow cycle. Returns the number of extra rows written."""
        return await propagate_header_bucket_readings(session, header_bucket_id, reading_row)

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
            raw_data=self._sanitize_readings(result.readings),
        )
        session.add(log)
        return log


@lru_cache(maxsize=16)
def model_column_names(model_cls: type[Any]) -> set[str]:
    """Return a cached set of SQLAlchemy column names for a model class."""
    return {column.name for column in model_cls.__table__.columns}


def filter_model_fields(
    model_cls: type[Any],
    values: dict[str, Any],
    *,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    """Keep only non-null keys that exist as columns on ``model_cls``."""
    excluded = exclude or set()
    allowed = model_column_names(model_cls)
    return {k: v for k, v in values.items() if k in allowed and k not in excluded and v is not None}


# ---- Connector registry ----

_registry: dict[str, type[BaseConnector]] = {}


def register_connector(connector_cls: type[BaseConnector]) -> type[BaseConnector]:
    """Decorator to register a connector class by its ``integration_type``."""
    _registry[connector_cls.integration_type] = connector_cls
    return connector_cls


def get_connector_class(integration_type: str) -> type[BaseConnector] | None:
    """Look up a registered connector class by type string."""
    return _registry.get(integration_type)


# ---- RDWC header bucket propagation ----


async def propagate_header_bucket_readings(
    session: AsyncSession,
    header_bucket_id: str,
    reading_row: Any,
) -> int:
    """For RDWC header buckets, duplicate the reading to all site buckets
    in the same grow cycle. Returns the number of extra rows written."""
    from app.grows.models import Bucket, BucketSensorReading, GrowCycle

    # Look up the header bucket and verify its role
    header = await session.get(Bucket, uuid.UUID(header_bucket_id))
    if not header or header.role != "header":
        return 0

    # Only propagate for RDWC grows (shared reservoir)
    grow = await session.get(GrowCycle, header.grow_cycle_id)
    if not grow or grow.grow_type != "rdwc":
        return 0

    # Find all site buckets in the same grow cycle
    stmt_result = await session.execute(
        select(Bucket).where(
            Bucket.grow_cycle_id == header.grow_cycle_id,
            Bucket.role == "site",
            Bucket.id != header.id,
        )
    )
    site_buckets = stmt_result.scalars().all()
    if not site_buckets:
        return 0

    propagated_values = {
        key: getattr(reading_row, key)
        for key in model_column_names(BucketSensorReading)
        if key not in {"id", "bucket_id"} and hasattr(reading_row, key)
    }
    payload = filter_model_fields(
        BucketSensorReading,
        propagated_values,
        exclude={"id", "bucket_id"},
    )

    count = 0
    for site in site_buckets:
        row = BucketSensorReading(
            bucket_id=site.id,
            **payload,
        )
        session.add(row)
        count += 1
    return count
