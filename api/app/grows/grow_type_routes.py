"""Grow type profiles API — list types, get profile details, stage configs."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.grows.grow_types import GROW_TYPE_PROFILES
from app.grows.grow_type_configs import get_grow_type_config

router = APIRouter()


@router.get("")
async def list_grow_types():
    """List all available grow types (summary)."""
    return [
        {"id": p["id"], "name": p["name"], "category": p["category"], "description": p["description"]}
        for p in GROW_TYPE_PROFILES
    ]


@router.get("/{grow_type_id}")
async def get_grow_type(grow_type_id: str):
    """Get full profile for a specific grow type."""
    for p in GROW_TYPE_PROFILES:
        if p["id"] == grow_type_id:
            return p
    raise HTTPException(status_code=404, detail="Grow type not found")


@router.get("/{grow_type_id}/config")
async def get_grow_type_config_endpoint(grow_type_id: str):
    """Get comprehensive stage-by-stage configuration for a grow type.

    Returns environmental targets, nutrient schedules, tasks, health checks,
    equipment checklists, quick reference, and troubleshooting for every stage.
    """
    config = get_grow_type_config(grow_type_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not available for this grow type")
    return config
