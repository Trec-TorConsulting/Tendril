"""Grow type profiles API — list types, get profile details."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.grows.grow_types import GROW_TYPE_PROFILES

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
