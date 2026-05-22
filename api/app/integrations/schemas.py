"""Pydantic schemas for the integrations API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Integration Config
# ---------------------------------------------------------------------------


class IntegrationCreate(BaseModel):
    type: str = Field(..., max_length=50, description="Integration type, e.g. pulse, ecowitt, home_assistant")
    name: str = Field(..., max_length=255)
    config: dict = Field(..., description="Integration-specific credentials and settings")
    enabled: bool = True
    poll_interval_s: int | None = Field(None, ge=60, description="Polling interval in seconds (min 60)")


class IntegrationUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    config: dict | None = None
    enabled: bool | None = None
    poll_interval_s: int | None = Field(None, ge=60)


class IntegrationResponse(BaseModel):
    id: UUID
    type: str
    name: str
    config: dict  # credentials redacted
    webhook_secret: str
    enabled: bool
    poll_interval_s: int | None
    last_synced_at: datetime | None
    error_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Device Map
# ---------------------------------------------------------------------------


class DeviceMapCreate(BaseModel):
    external_id: str = Field(..., max_length=255)
    external_name: str | None = Field(None, max_length=255)
    tent_id: UUID | None = None
    bucket_id: UUID | None = None
    sensor_mapping: dict = Field(default_factory=dict, description="Field map: {ext_field: tendril_column}")
    enabled: bool = True


class DeviceMapUpdate(BaseModel):
    external_name: str | None = Field(None, max_length=255)
    tent_id: UUID | None = None
    bucket_id: UUID | None = None
    sensor_mapping: dict | None = None
    enabled: bool | None = None


class DeviceMapResponse(BaseModel):
    id: UUID
    integration_id: UUID
    external_id: str
    external_name: str | None
    tent_id: UUID | None
    bucket_id: UUID | None
    sensor_mapping: dict
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Sync Log
# ---------------------------------------------------------------------------


class SyncLogResponse(BaseModel):
    id: UUID
    integration_id: UUID
    status: str
    readings_count: int
    error_message: str | None
    raw_data: list | dict | None = None
    synced_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class DiscoveredDeviceResponse(BaseModel):
    external_id: str
    name: str
    device_type: str
    latest_reading: dict | None = None
