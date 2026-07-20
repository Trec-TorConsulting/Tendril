"""Reference data API — strain autocomplete + nutrient lookup + feed charts +
ESPHome templates + nutrient knowledge base.

This module is HTTP-only. All persistence, YAML rendering, and filtering
live in ``app.reference.service``.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.auth.middleware import CurrentUser, get_current_user
from app.database import async_session_factory
from app.reference import service

router = APIRouter()


class ReferenceStrainResponse(BaseModel):
    id: UUID
    name: str
    breeder: str | None
    genetics: str | None
    strain_type: str | None = None
    indica_pct: int | None = None
    sativa_pct: int | None = None
    thc_pct: float | None
    thc_min: float | None = None
    thc_max: float | None = None
    cbd_pct: float | None
    cbd_min: float | None = None
    cbd_max: float | None = None
    terpenes: list[str] | None = None
    effects: list[str] | None = None
    flavors: list[str] | None = None
    flowering_min_weeks: float | None = None
    flowering_max_weeks: float | None = None
    yield_indoor: str | None = None
    yield_outdoor: str | None = None
    description: str | None
    sources: list[str] | None = None
    last_verified: date | None = None
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


# ─── Strains ──────────────────────────────────────────────────────────────────


@router.get("/strains", response_model=list[ReferenceStrainResponse])
async def search_reference_strains(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    q: str = Query(min_length=2, max_length=100),
    limit: int = Query(default=20, le=50),
):
    """Autocomplete strain names from the reference database."""
    async with async_session_factory() as session:
        return await service.search_reference_strains(session, query=q, limit=limit)


@router.get("/strains/{strain_id}", response_model=ReferenceStrainResponse)
async def get_reference_strain(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get a reference strain from the global database by ID."""
    async with async_session_factory() as session:
        strain = await service.get_reference_strain(session, strain_id)
        if strain is None:
            raise HTTPException(status_code=404, detail="Reference strain not found")
        return strain


# ─── Nutrients ────────────────────────────────────────────────────────────────


@router.get("/nutrients/barcode/{barcode}", response_model=NutrientProductResponse)
async def lookup_nutrient_barcode(
    barcode: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Look up a nutrient product by barcode."""
    async with async_session_factory() as session:
        product = await service.get_nutrient_product_by_barcode(session, barcode)
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
        return await service.search_nutrient_products(session, query=q, limit=limit)


# ─── Feed Charts ──────────────────────────────────────────────────────────────


@router.get("/feed-charts")
async def list_feed_charts(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    brand: str | None = None,
    medium: str | None = None,
):
    """List nutrient brand feed charts. Optionally filter by brand or medium."""
    async with async_session_factory() as session:
        charts = await service.list_feed_charts(session, brand=brand)

    filtered = service.filter_feed_charts_by_medium(charts, medium)
    return [
        {
            "brand": c.brand,
            "line": c.line,
            "medium": c.medium,
            "products": c.products,
            "schedule": c.schedule,
            "notes": c.notes,
        }
        for c in filtered
    ]


@router.get("/feed-charts/brands")
async def list_feed_chart_brands(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List available nutrient brand names."""
    async with async_session_factory() as session:
        return await service.list_feed_chart_brands(session)


# ─── ESPHome Templates ────────────────────────────────────────────────────────


@router.get("/esphome/templates")
async def list_esphome_templates(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List available ESPHome sensor config templates."""
    async with async_session_factory() as session:
        templates = await service.list_esphome_templates(session)
    return [
        {
            "id": t.template_id,
            "name": t.name,
            "description": t.description,
            "sensors": t.sensors,
        }
        for t in templates
    ]


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
    async with async_session_factory() as session:
        tmpl = await service.get_esphome_template_by_template_id(session, body.template_id)

    if tmpl is None:
        raise HTTPException(status_code=400, detail=f"Unknown template: {body.template_id}")

    yaml_output = service.render_esphome_yaml(
        tmpl,
        device_name=body.device_name,
        mqtt_host=body.mqtt_host,
        mqtt_user=body.mqtt_user,
        mqtt_password=body.mqtt_password,
        wifi_ssid=body.wifi_ssid,
        wifi_password=body.wifi_password,
    )
    return {"yaml": yaml_output, "template_id": body.template_id}


# ─── Strain Database Sync ──────────────────────────────────────────────────────


@router.post("/strains/sync")
async def sync_strains(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Sync reference strains from seed data. Requires admin role."""
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    async with async_session_factory() as session:
        added = await service.sync_seed_reference_strains(session)

    return {"added": added, "status": "ok"}


# ─── Nutrient Knowledge Base ──────────────────────────────────────────────────


@router.get("/knowledge")
async def get_nutrient_knowledge(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get the complete nutrient knowledge base (DIY recipes, emergency subs, pH guides, methodology)."""
    async with async_session_factory() as session:
        grouped = await service.get_nutrient_knowledge_grouped(session)
    return {
        "diy_recipes": grouped.get("diy_recipe", []),
        "emergency_substitutions": grouped.get("emergency_substitution", []),
        "ph_alternatives": grouped.get("ph_alternative", []),
        "methodology_guides": grouped.get("methodology_guide", []),
    }


@router.get("/knowledge/diy-recipes")
async def get_diy_recipes(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    category: str | None = None,
    difficulty: str | None = None,
):
    """Get DIY/homemade nutrient recipes. Optionally filter by category or difficulty."""
    async with async_session_factory() as session:
        return await service.list_diy_recipes(session, category=category, difficulty=difficulty)


@router.get("/knowledge/emergency")
async def get_emergency_substitutions(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    deficiency: str | None = None,
):
    """Get emergency nutrient substitution guides. Optionally filter by deficiency type."""
    async with async_session_factory() as session:
        return await service.list_emergency_substitutions(session, deficiency=deficiency)


@router.get("/knowledge/ph-alternatives")
async def get_ph_alternatives(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    direction: str | None = None,
):
    """Get pH management alternatives (household/DIY). Optionally filter by direction (up/down)."""
    async with async_session_factory() as session:
        return await service.list_ph_alternatives(session, direction=direction)


@router.get("/knowledge/methodology")
async def get_methodology_guides(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    approach: str | None = None,
):
    """Get growing methodology guides (sterile, organic, hybrid, water quality)."""
    async with async_session_factory() as session:
        return await service.list_methodology_guides(session, approach=approach)
