"""Reference data API — strain autocomplete + nutrient barcode lookup."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user
from app.database import async_session_factory
from app.grows.models import ReferenceStrain, NutrientProduct

router = APIRouter()


class ReferenceStrainResponse(BaseModel):
    id: UUID
    name: str
    breeder: str | None
    genetics: str | None
    thc_pct: float | None
    cbd_pct: float | None
    description: str | None
    model_config = {"from_attributes": True}


class NutrientProductResponse(BaseModel):
    id: UUID
    barcode: str
    name: str
    brand: str | None
    npk: str | None
    nutrients: dict | None
    image_url: str | None
    source: str
    model_config = {"from_attributes": True}


@router.get("/strains", response_model=list[ReferenceStrainResponse])
async def search_reference_strains(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    q: str = Query(min_length=2, max_length=100),
    limit: int = Query(default=20, le=50),
):
    """Autocomplete strain names from the reference database."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ReferenceStrain)
            .where(ReferenceStrain.name.ilike(f"%{q}%"))
            .order_by(ReferenceStrain.name)
            .limit(limit)
        )
        return result.scalars().all()


@router.get("/strains/{strain_id}", response_model=ReferenceStrainResponse)
async def get_reference_strain(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get a reference strain from the global database by ID."""
    async with async_session_factory() as session:
        strain = await session.get(ReferenceStrain, strain_id)
        if strain is None:
            raise HTTPException(status_code=404, detail="Reference strain not found")
        return strain


@router.get("/nutrients/barcode/{barcode}", response_model=NutrientProductResponse)
async def lookup_nutrient_barcode(
    barcode: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Look up a nutrient product by barcode."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(NutrientProduct).where(NutrientProduct.barcode == barcode)
        )
        product = result.scalar_one_or_none()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found for barcode")
        return product


@router.get("/nutrients", response_model=list[NutrientProductResponse])
async def search_nutrients(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    q: str = Query(min_length=2, max_length=100),
    limit: int = Query(default=20, le=50),
):
    """Search nutrient products by name or brand."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(NutrientProduct)
            .where(
                NutrientProduct.name.ilike(f"%{q}%")
                | NutrientProduct.brand.ilike(f"%{q}%")
            )
            .order_by(NutrientProduct.name)
            .limit(limit)
        )
        return result.scalars().all()
