"""Plot grid API — garden bed layout designer for outdoor soil grows."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import GrowCycle, PlotCell, PlotGrid

router = APIRouter()


# ---------- Schemas ----------


class PlotGridUpsert(BaseModel):
    rows: int = Field(ge=1, le=50)
    cols: int = Field(ge=1, le=50)
    cell_size_inches: int = Field(default=12, ge=1, le=96)
    orientation: str = Field(default="north", pattern=r"^(north|south|east|west)$")
    notes: str | None = None


class CellUpdate(BaseModel):
    row: int = Field(ge=0)
    col: int = Field(ge=0)
    cell_type: str = Field(default="empty", pattern=r"^(plant|companion|path|empty|sensor|irrigation)$")
    bucket_id: UUID | None = None
    companion_plant: str | None = None
    device_id: str | None = None
    irrigation_zone: str | None = None
    sun_zone: str | None = Field(default=None, pattern=r"^(full_sun|partial_sun|partial_shade|full_shade)$")
    notes: str | None = None


class CellBatchUpdate(BaseModel):
    cells: list[CellUpdate]


class CellResponse(BaseModel):
    id: UUID
    row: int
    col: int
    cell_type: str
    bucket_id: UUID | None
    companion_plant: str | None
    device_id: str | None
    irrigation_zone: str | None
    sun_zone: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class PlotGridResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    rows: int
    cols: int
    cell_size_inches: int
    orientation: str
    notes: str | None
    cells: list[CellResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Endpoints ----------


@router.put("/{grow_id}/plot", response_model=PlotGridResponse, status_code=200)
async def upsert_plot_grid(
    grow_id: UUID,
    body: PlotGridUpsert,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create or update the garden plot grid for a grow."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    result = await session.execute(select(PlotGrid).where(PlotGrid.grow_cycle_id == grow_id))
    grid = result.scalar_one_or_none()

    if grid is None:
        grid = PlotGrid(
            tenant_id=user.tenant_id,
            grow_cycle_id=grow_id,
            **body.model_dump(),
        )
        session.add(grid)
    else:
        for k, v in body.model_dump().items():
            setattr(grid, k, v)
        grid.updated_at = datetime.now(UTC)
        # Remove cells outside new dimensions
        await session.execute(
            delete(PlotCell).where(
                PlotCell.plot_grid_id == grid.id,
                (PlotCell.row >= body.rows) | (PlotCell.col >= body.cols),
            )
        )

    await session.commit()
    await session.refresh(grid, ["cells"])
    return grid


@router.get("/{grow_id}/plot", response_model=PlotGridResponse)
async def get_plot_grid(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the garden plot grid with all cells for a grow."""
    result = await session.execute(select(PlotGrid).where(PlotGrid.grow_cycle_id == grow_id))
    grid = result.scalar_one_or_none()
    if grid is None:
        raise HTTPException(status_code=404, detail="Plot grid not found")
    await session.refresh(grid, ["cells"])
    return grid


@router.patch("/{grow_id}/plot/cells", response_model=list[CellResponse])
async def batch_update_cells(
    grow_id: UUID,
    body: CellBatchUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Batch create or update cells in the plot grid."""
    result = await session.execute(select(PlotGrid).where(PlotGrid.grow_cycle_id == grow_id))
    grid = result.scalar_one_or_none()
    if grid is None:
        raise HTTPException(status_code=404, detail="Plot grid not found")

    updated: list[PlotCell] = []
    for cell_data in body.cells:
        if cell_data.row >= grid.rows or cell_data.col >= grid.cols:
            raise HTTPException(status_code=400, detail=f"Cell ({cell_data.row},{cell_data.col}) outside grid bounds")

        result = await session.execute(
            select(PlotCell).where(
                PlotCell.plot_grid_id == grid.id,
                PlotCell.row == cell_data.row,
                PlotCell.col == cell_data.col,
            )
        )
        cell = result.scalar_one_or_none()

        if cell is None:
            cell = PlotCell(  # type: ignore[assignment]
                tenant_id=user.tenant_id,
                plot_grid_id=grid.id,
                **cell_data.model_dump(),
            )
            session.add(cell)
        else:
            for k, v in cell_data.model_dump().items():
                setattr(cell, k, v)
        updated.append(cell)  # type: ignore[arg-type]

    grid.updated_at = datetime.now(UTC)
    await session.commit()
    for c in updated:
        await session.refresh(c)
    return updated


@router.delete("/{grow_id}/plot", status_code=204)
async def delete_plot_grid(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete the entire plot grid for a grow."""
    result = await session.execute(select(PlotGrid).where(PlotGrid.grow_cycle_id == grow_id))
    grid = result.scalar_one_or_none()
    if grid is None:
        raise HTTPException(status_code=404, detail="Plot grid not found")
    await session.delete(grid)
    await session.commit()
