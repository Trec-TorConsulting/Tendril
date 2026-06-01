"""Field Canvas API — CRUD for draw.io-style garden layout."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.grows.models import FieldCanvas, GrowCycle

router = APIRouter()


class CanvasDataPayload(BaseModel):
    canvas_data: dict
    name: str | None = None


class FieldCanvasResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    name: str
    canvas_data: dict
    thumbnail_key: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("/grows/{grow_id}/field-canvas", response_model=FieldCanvasResponse)
async def get_field_canvas(
    grow_id: UUID,
    session: AsyncSession = Depends(get_tenant_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Get the field canvas for a grow cycle."""
    canvas = (
        await session.execute(select(FieldCanvas).where(FieldCanvas.grow_cycle_id == grow_id))
    ).scalar_one_or_none()

    if not canvas:
        raise HTTPException(status_code=404, detail="No canvas found for this grow")

    return canvas


@router.put("/grows/{grow_id}/field-canvas", response_model=FieldCanvasResponse)
async def upsert_field_canvas(
    grow_id: UUID,
    payload: CanvasDataPayload,
    session: AsyncSession = Depends(get_tenant_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Create or update the field canvas for a grow cycle."""
    # Verify grow exists and belongs to tenant
    grow = (await session.execute(select(GrowCycle).where(GrowCycle.id == grow_id))).scalar_one_or_none()

    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    canvas = (
        await session.execute(select(FieldCanvas).where(FieldCanvas.grow_cycle_id == grow_id))
    ).scalar_one_or_none()

    if canvas:
        canvas.canvas_data = payload.canvas_data
        if payload.name:
            canvas.name = payload.name
        canvas.updated_at = datetime.now(UTC)
    else:
        canvas = FieldCanvas(
            tenant_id=grow.tenant_id,
            grow_cycle_id=grow_id,
            name=payload.name or "Main Field",
            canvas_data=payload.canvas_data,
        )
        session.add(canvas)

    await session.commit()
    await session.refresh(canvas)
    return canvas


@router.delete("/grows/{grow_id}/field-canvas", status_code=204)
async def delete_field_canvas(
    grow_id: UUID,
    session: AsyncSession = Depends(get_tenant_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Delete the field canvas for a grow cycle."""
    canvas = (
        await session.execute(select(FieldCanvas).where(FieldCanvas.grow_cycle_id == grow_id))
    ).scalar_one_or_none()

    if not canvas:
        raise HTTPException(status_code=404, detail="No canvas found")

    await session.delete(canvas)
    await session.commit()
