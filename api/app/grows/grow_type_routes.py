"""Grow type profiles API — list types, get profile details, stage configs."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.middleware import CurrentUser, get_current_user
from app.database import async_session_factory

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def list_grow_types(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List all available grow types (summary)."""
    from app.config_management.service.grow_types import list_profiles

    async with async_session_factory() as session:
        profiles = await list_profiles(session)
        return [{"id": p["slug"], "name": p["name"], "description": p["description"]} for p in profiles]


@router.get("/{grow_type_id}")
async def get_grow_type(
    grow_type_id: str,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get full profile for a specific grow type."""
    from app.config_management.service.grow_types import get_profile

    async with async_session_factory() as session:
        profile = await get_profile(session, grow_type_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Grow type not found")
        return profile


VALID_SCALES = {"solo", "small_tent", "multi_tent", "commercial_room", "warehouse"}
VALID_STRAIN_TYPES = {"autoflower", "photoperiod"}


@router.get("/{grow_type_id}/config")
async def get_grow_type_config_endpoint(
    grow_type_id: str,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    scale: Annotated[
        str | None,
        Query(description="Filter to a specific scale tier (solo, small_tent, multi_tent, commercial_room, warehouse)"),
    ] = None,
    strain_type: Annotated[
        str | None, Query(description="Filter strain-specific data (autoflower or photoperiod)")
    ] = None,
):
    """Get comprehensive stage-by-stage configuration for a grow type.

    Returns environmental targets, nutrient schedules, tasks, health checks,
    equipment checklists, quick reference, and troubleshooting for every stage.

    Optional query params:
      - scale: Filter scale_tiers to only the matching tier
      - strain_type: Filter strain_adjustments and include strain-specific duration/notes
    """
    from app.config_management.service.grow_types import get_full_config

    async with async_session_factory() as session:
        config = await get_full_config(session, grow_type_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not available for this grow type")

    if scale and scale not in VALID_SCALES:
        raise HTTPException(status_code=400, detail=f"Invalid scale. Must be one of: {', '.join(sorted(VALID_SCALES))}")
    if strain_type and strain_type not in VALID_STRAIN_TYPES:
        raise HTTPException(
            status_code=400, detail=f"Invalid strain_type. Must be one of: {', '.join(sorted(VALID_STRAIN_TYPES))}"
        )

    result = dict(config)

    if scale:
        result["scale_tiers"] = [t for t in config.get("scale_tiers", []) if t.get("id") == scale]

    if strain_type:
        adj = config.get("strain_adjustments", {})
        result["strain_adjustments"] = {strain_type: adj[strain_type]} if strain_type in adj else {}
        duration_key = f"duration_days_{strain_type[:4]}"
        notes_key = f"{strain_type}_notes"
        filtered_stages = []
        for stage in config.get("stages", []):
            stage_copy = dict(stage)
            if duration_key in stage_copy:
                stage_copy["duration_days_filtered"] = stage_copy[duration_key]
            if notes_key in stage_copy:
                stage_copy["strain_notes"] = stage_copy[notes_key]
            filtered_stages.append(stage_copy)
        result["stages"] = filtered_stages

    return result


@router.get("/{grow_type_id}/thresholds")
async def get_grow_type_thresholds(
    grow_type_id: str,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get monitoring thresholds for a grow type — suitable for automation integration."""
    from app.config_management.service.grow_types import get_full_config

    async with async_session_factory() as session:
        config = await get_full_config(session, grow_type_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not available for this grow type")

    return {
        "grow_type_id": grow_type_id,
        "thresholds": config.get("monitoring_thresholds", {}),
    }


@router.get("/{grow_type_id}/equipment")
async def get_grow_type_equipment(
    grow_type_id: str,
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    scale: Annotated[str | None, Query(description="Filter equipment recommendations by scale tier")] = None,
):
    """Get equipment checklist for a grow type, optionally filtered by scale."""
    from app.config_management.service.grow_types import get_full_config

    async with async_session_factory() as session:
        config = await get_full_config(session, grow_type_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not available for this grow type")

    if scale and scale not in VALID_SCALES:
        raise HTTPException(status_code=400, detail=f"Invalid scale. Must be one of: {', '.join(sorted(VALID_SCALES))}")

    equipment = config.get("equipment", [])

    if scale:
        tiers = [t for t in config.get("scale_tiers", []) if t.get("id") == scale]
        return {
            "grow_type_id": grow_type_id,
            "scale": scale,
            "scale_tier": tiers[0] if tiers else None,
            "equipment": equipment,
        }

    return {"grow_type_id": grow_type_id, "equipment": equipment}
