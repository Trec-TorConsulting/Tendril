"""Reference data API — strain autocomplete + nutrient barcode lookup."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from app.auth.middleware import CurrentUser, get_current_user
from app.database import async_session_factory
from app.grows.models import NutrientProduct, ReferenceStrain

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
        result = await session.execute(select(NutrientProduct).where(NutrientProduct.barcode == barcode))
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
            .where(NutrientProduct.name.ilike(f"%{q}%") | NutrientProduct.brand.ilike(f"%{q}%"))
            .order_by(NutrientProduct.name)
            .limit(limit)
        )
        return result.scalars().all()


# ─── Feed Charts (static reference data) ──────────────────────────────────────


@router.get("/feed-charts")
async def list_feed_charts(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    brand: str | None = None,
    medium: str | None = None,
):
    """List nutrient brand feed charts. Optionally filter by brand or medium."""
    from app.reference.feed_charts import get_all_charts

    charts = get_all_charts()
    if brand:
        charts = [c for c in charts if c["brand"].lower() == brand.lower()]
    if medium:
        charts = [c for c in charts if medium.lower() in c["medium"]]
    return charts


@router.get("/feed-charts/brands")
async def list_feed_chart_brands(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List available nutrient brand names."""
    from app.reference.feed_charts import get_brands

    return get_brands()


# ─── ESPHome Templates ─────────────────────────────────────────────────────────


@router.get("/esphome/templates")
async def list_esphome_templates(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List available ESPHome sensor config templates."""
    from app.reference.esphome_templates import list_templates

    return list_templates()


class ESPHomeGenerateRequest(BaseModel):
    template_id: str
    device_name: str
    mqtt_host: str
    mqtt_user: str
    mqtt_password: str
    wifi_ssid: str
    wifi_password: str


@router.post("/esphome/generate")
async def generate_esphome_config(
    body: ESPHomeGenerateRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Generate an ESPHome YAML configuration from a template."""
    from app.reference.esphome_templates import generate_yaml

    try:
        yaml_output = generate_yaml(
            template_id=body.template_id,
            device_name=body.device_name,
            mqtt_host=body.mqtt_host,
            mqtt_user=body.mqtt_user,
            mqtt_password=body.mqtt_password,
            wifi_ssid=body.wifi_ssid,
            wifi_password=body.wifi_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"yaml": yaml_output, "template_id": body.template_id}


# ─── Strain Database Sync ──────────────────────────────────────────────────────


@router.post("/strains/sync")
async def sync_strains(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Sync reference strains from seed data. Requires admin role."""
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    from app.reference.strain_sync import sync_seed_strains

    async with async_session_factory() as session:
        added = await sync_seed_strains(session)

    return {"added": added, "status": "ok"}
