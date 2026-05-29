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


# ─── Feed Charts (DB-backed reference data) ───────────────────────────────────


@router.get("/feed-charts")
async def list_feed_charts(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    brand: str | None = None,
    medium: str | None = None,
):
    """List nutrient brand feed charts. Optionally filter by brand or medium."""
    from app.reference.models import FeedChart

    async with async_session_factory() as session:
        query = select(FeedChart)
        if brand:
            query = query.where(FeedChart.brand.ilike(brand))
        result = await session.execute(query)
        charts = result.scalars().all()

    out = []
    for c in charts:
        if medium and medium.lower() not in (c.medium or []):
            continue
        out.append(
            {
                "brand": c.brand,
                "line": c.line,
                "medium": c.medium,
                "products": c.products,
                "schedule": c.schedule,
                "notes": c.notes,
            }
        )
    return out


@router.get("/feed-charts/brands")
async def list_feed_chart_brands(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List available nutrient brand names."""
    from sqlalchemy import distinct

    from app.reference.models import FeedChart

    async with async_session_factory() as session:
        result = await session.execute(select(distinct(FeedChart.brand)).order_by(FeedChart.brand))
        return [row[0] for row in result.all()]


# ─── ESPHome Templates (DB-backed) ─────────────────────────────────────────────


@router.get("/esphome/templates")
async def list_esphome_templates(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List available ESPHome sensor config templates."""
    from app.reference.models import ESPHomeTemplate

    async with async_session_factory() as session:
        result = await session.execute(select(ESPHomeTemplate))
        templates = result.scalars().all()
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
    from app.reference.models import ESPHomeTemplate

    async with async_session_factory() as session:
        result = await session.execute(select(ESPHomeTemplate).where(ESPHomeTemplate.template_id == body.template_id))
        tmpl = result.scalar_one_or_none()

    if tmpl is None:
        raise HTTPException(status_code=400, detail=f"Unknown template: {body.template_id}")

    device_slug = body.device_name.lower().replace(" ", "-").replace("_", "-")

    yaml_output = f"""# ESPHome config generated by Tendril
# Template: {tmpl.name}
# Sensors: {", ".join(tmpl.sensors)}

esphome:
  name: {device_slug}
  friendly_name: "{body.device_name}"

esp32:
  board: {tmpl.board}

wifi:
  ssid: "{body.wifi_ssid}"
  password: "{body.wifi_password}"
  ap:
    ssid: "{body.device_name} Fallback"
    password: "tendril-setup"

mqtt:
  broker: "{body.mqtt_host}"
  username: "{body.mqtt_user}"
  password: "{body.mqtt_password}"
  topic_prefix: "tendril/{device_slug}"
  discovery: false

logger:
  level: INFO

ota:
  platform: esphome
{tmpl.yaml_body}"""

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


# ─── Nutrient Knowledge Base (DB-backed) ──────────────────────────────────────


@router.get("/knowledge")
async def get_nutrient_knowledge(
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get the complete nutrient knowledge base (DIY recipes, emergency subs, pH guides, methodology)."""
    from app.reference.models import NutrientKnowledge

    async with async_session_factory() as session:
        result = await session.execute(select(NutrientKnowledge))
        entries = result.scalars().all()

    grouped: dict[str, list] = {}
    for e in entries:
        grouped.setdefault(e.category, []).append(e.data)
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
    from app.reference.models import NutrientKnowledge

    async with async_session_factory() as session:
        result = await session.execute(select(NutrientKnowledge).where(NutrientKnowledge.category == "diy_recipe"))
        entries = result.scalars().all()

    recipes = [e.data for e in entries]
    if category:
        recipes = [r for r in recipes if r.get("category") == category]
    if difficulty:
        recipes = [r for r in recipes if r.get("difficulty") == difficulty]
    return recipes


@router.get("/knowledge/emergency")
async def get_emergency_substitutions(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    deficiency: str | None = None,
):
    """Get emergency nutrient substitution guides. Optionally filter by deficiency type."""
    from app.reference.models import NutrientKnowledge

    async with async_session_factory() as session:
        result = await session.execute(
            select(NutrientKnowledge).where(NutrientKnowledge.category == "emergency_substitution")
        )
        entries = result.scalars().all()

    subs = [e.data for e in entries]
    if deficiency:
        subs = [s for s in subs if deficiency.lower() in s.get("id", "")]
    return subs


@router.get("/knowledge/ph-alternatives")
async def get_ph_alternatives(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    direction: str | None = None,
):
    """Get pH management alternatives (household/DIY). Optionally filter by direction (up/down)."""
    from app.reference.models import NutrientKnowledge

    async with async_session_factory() as session:
        result = await session.execute(select(NutrientKnowledge).where(NutrientKnowledge.category == "ph_alternative"))
        entries = result.scalars().all()

    alts = [e.data for e in entries]
    if direction:
        alts = [a for a in alts if a.get("direction") == direction.lower()]
    return alts


@router.get("/knowledge/methodology")
async def get_methodology_guides(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    approach: str | None = None,
):
    """Get growing methodology guides (sterile, organic, hybrid, water quality)."""
    from app.reference.models import NutrientKnowledge

    async with async_session_factory() as session:
        result = await session.execute(
            select(NutrientKnowledge).where(NutrientKnowledge.category == "methodology_guide")
        )
        entries = result.scalars().all()

    guides = [e.data for e in entries]
    if approach:
        guides = [g for g in guides if g.get("approach") == approach.lower()]
    return guides
