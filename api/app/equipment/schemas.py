"""Pydantic schemas for equipment control API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.equipment.models import CAPABILITIES, EQUIPMENT_TYPES, PROTOCOLS


class EquipmentCreate(BaseModel):
    """Schema for creating new controllable equipment."""

    name: str = Field(..., min_length=1, max_length=255)
    tent_id: str | None = None
    equipment_type: str
    protocol: str
    protocol_config: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[str] = Field(default_factory=lambda: ["on_off"])
    max_on_minutes: int | None = None
    cooldown_minutes: int = 0
    conflicts_with: list[str] = Field(default_factory=list)

    @field_validator("equipment_type")
    @classmethod
    def validate_equipment_type(cls, v: str) -> str:
        if v not in EQUIPMENT_TYPES:
            raise ValueError(f"Invalid equipment_type. Must be one of: {sorted(EQUIPMENT_TYPES)}")
        return v

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v: str) -> str:
        if v not in PROTOCOLS:
            raise ValueError(f"Invalid protocol. Must be one of: {sorted(PROTOCOLS)}")
        return v

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, v: list[str]) -> list[str]:
        invalid = set(v) - CAPABILITIES
        if invalid:
            raise ValueError(f"Invalid capabilities: {invalid}. Must be from: {sorted(CAPABILITIES)}")
        return v

    @field_validator("max_on_minutes")
    @classmethod
    def validate_max_on(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("max_on_minutes must be at least 1")
        return v

    @field_validator("cooldown_minutes")
    @classmethod
    def validate_cooldown(cls, v: int) -> int:
        if v < 0:
            raise ValueError("cooldown_minutes must be non-negative")
        return v


class EquipmentUpdate(BaseModel):
    """Schema for updating existing equipment."""

    name: str | None = Field(None, min_length=1, max_length=255)
    tent_id: str | None = None
    equipment_type: str | None = None
    protocol: str | None = None
    protocol_config: dict[str, Any] | None = None
    capabilities: list[str] | None = None
    max_on_minutes: int | None = None
    cooldown_minutes: int | None = None
    conflicts_with: list[str] | None = None
    enabled: bool | None = None

    @field_validator("equipment_type")
    @classmethod
    def validate_equipment_type(cls, v: str | None) -> str | None:
        if v is not None and v not in EQUIPMENT_TYPES:
            raise ValueError(f"Invalid equipment_type. Must be one of: {sorted(EQUIPMENT_TYPES)}")
        return v

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v: str | None) -> str | None:
        if v is not None and v not in PROTOCOLS:
            raise ValueError(f"Invalid protocol. Must be one of: {sorted(PROTOCOLS)}")
        return v

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            invalid = set(v) - CAPABILITIES
            if invalid:
                raise ValueError(f"Invalid capabilities: {invalid}. Must be from: {sorted(CAPABILITIES)}")
        return v


class EquipmentResponse(BaseModel):
    """Response schema for equipment records."""

    id: str
    tenant_id: str
    tent_id: str | None
    name: str
    equipment_type: str
    protocol: str
    protocol_config: dict[str, Any]
    capabilities: list[str]
    requested_state: dict[str, Any]
    confirmed_state: dict[str, Any]
    last_confirmed_at: datetime | None
    max_on_minutes: int | None
    cooldown_minutes: int
    conflicts_with: list[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EquipmentCommand(BaseModel):
    """Schema for sending a command to equipment."""

    action: str = Field(..., description="Command action: on, off, toggle, set_brightness")
    value: int | None = Field(None, description="Value for dimmer commands (0-100)")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        valid_actions = {"on", "off", "toggle", "set_brightness"}
        if v not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of: {sorted(valid_actions)}")
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("value must be between 0 and 100")
        return v


class EquipmentCommandResponse(BaseModel):
    """Response after sending a command."""

    equipment_id: str
    action: str
    success: bool
    requested_state: dict[str, Any]
    message: str | None = None


class StateLogResponse(BaseModel):
    """Response schema for equipment state log entries."""

    id: str
    equipment_id: str
    action: str
    source: str
    state_before: dict[str, Any] | None
    state_after: dict[str, Any] | None
    metadata_: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TestConnectionResponse(BaseModel):
    """Response for test-connection endpoint."""

    reachable: bool
    protocol: str
    message: str
    device_info: dict[str, Any] | None = None
