"""Nutrition API routes — brands, lines, products, feed charts, additives, recipes, profiles."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.nutrition import (
    CustomNutrient,
    GrowNutrientProfile,
    NutrientAdditive,
    NutrientBrand,
    NutrientConflict,
    NutrientFeedChart,
    NutrientLine,
    OrganicRecipe,
)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════════════════


class BrandResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None
    website: str | None
    logo_url: str | None
    country: str | None
    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    product_type: str
    npk: str | None
    description: str | None
    usage_notes: str | None
    is_required: bool
    sort_order: int
    model_config = {"from_attributes": True}


class FeedChartResponse(BaseModel):
    id: UUID
    week_number: int
    stage: str
    phase_name: str
    doses: list[dict]
    target_ec_min: float | None
    target_ec_max: float | None
    target_ph_min: float | None
    target_ph_max: float | None
    target_ppm_500: float | None
    notes: str | None
    model_config = {"from_attributes": True}


class LineResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None
    line_type: str
    part_count: int
    format: str
    difficulty: str
    ph_buffered: bool
    grow_type_slugs: list[str]
    brand: BrandResponse | None = None
    products: list[ProductResponse] = []
    feed_charts: list[FeedChartResponse] = []
    model_config = {"from_attributes": True}


class LineSummaryResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None
    line_type: str
    part_count: int
    format: str
    difficulty: str
    ph_buffered: bool
    grow_type_slugs: list[str]
    brand_name: str
    brand_slug: str
    model_config = {"from_attributes": True}


class AdditiveResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    category: str
    description: str | None
    dose_ml_per_gallon: float | None
    dose_grams_per_gallon: float | None
    when_to_use: str | None
    grow_type_slugs: list[str]
    brand_name: str | None = None
    model_config = {"from_attributes": True}


class ConflictResponse(BaseModel):
    id: UUID
    item_a_type: str
    item_a_slug: str
    item_b_type: str
    item_b_slug: str
    severity: str
    reason: str
    recommendation: str | None
    model_config = {"from_attributes": True}


class RecipeResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    category: str
    description: str | None
    ingredients: list[dict]
    instructions: str
    brew_time_hours: float | None
    application_rate: str | None
    frequency: str | None
    best_for_stages: list[str] | None
    grow_type_slugs: list[str]
    warnings: str | None
    model_config = {"from_attributes": True}


class CustomNutrientCreate(BaseModel):
    name: str = Field(max_length=200)
    nutrient_type: str = Field(max_length=50)
    npk: str | None = None
    dose_ml_per_gallon: float | None = None
    dose_grams_per_gallon: float | None = None
    ingredients: list[dict] | None = None
    instructions: str | None = None
    notes: str | None = None


class CustomNutrientUpdate(BaseModel):
    name: str | None = None
    nutrient_type: str | None = None
    npk: str | None = None
    dose_ml_per_gallon: float | None = None
    dose_grams_per_gallon: float | None = None
    ingredients: list[dict] | None = None
    instructions: str | None = None
    notes: str | None = None


class CustomNutrientResponse(BaseModel):
    id: UUID
    name: str
    nutrient_type: str
    npk: str | None
    dose_ml_per_gallon: float | None
    dose_grams_per_gallon: float | None
    ingredients: list[dict] | None
    instructions: str | None
    notes: str | None
    model_config = {"from_attributes": True}


class GrowNutrientProfileCreate(BaseModel):
    grow_cycle_id: UUID
    primary_line_id: UUID | None = None
    secondary_line_id: UUID | None = None
    selected_products: list[str] | None = None
    selected_additives: list[str] | None = None
    selected_recipes: list[str] | None = None
    custom_nutrient_ids: list[UUID] | None = None
    strength_pct: int = 100
    approach: str = "week_by_week"
    notes: str | None = None


class GrowNutrientProfileUpdate(BaseModel):
    primary_line_id: UUID | None = None
    secondary_line_id: UUID | None = None
    selected_products: list[str] | None = None
    selected_additives: list[str] | None = None
    selected_recipes: list[str] | None = None
    custom_nutrient_ids: list[UUID] | None = None
    strength_pct: int | None = None
    approach: str | None = None
    notes: str | None = None


class GrowNutrientProfileResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    primary_line_id: UUID | None
    secondary_line_id: UUID | None
    selected_products: list[str] | None
    selected_additives: list[str] | None
    selected_recipes: list[str] | None
    custom_nutrient_ids: list[UUID] | None
    strength_pct: int
    approach: str
    notes: str | None
    model_config = {"from_attributes": True}


class FeedingRecommendationResponse(BaseModel):
    """What the user should feed THIS week based on their profile."""

    week_number: int
    stage: str
    phase_name: str
    primary_line_doses: list[dict]
    secondary_line_doses: list[dict]
    additives: list[dict]
    recipes: list[dict]
    custom_nutrients: list[dict]
    target_ec_min: float | None
    target_ec_max: float | None
    target_ph_min: float | None
    target_ph_max: float | None
    conflicts: list[ConflictResponse]
    notes: str | None


# ═══════════════════════════════════════════════════════════════════════════════
# Brand / Line / Product Endpoints (Public reference data)
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/brands", response_model=list[BrandResponse])
async def list_brands(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """List all nutrient brands."""
    result = await session.execute(select(NutrientBrand).order_by(NutrientBrand.name))
    return result.scalars().all()


@router.get("/brands/{slug}", response_model=BrandResponse)
async def get_brand(
    slug: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single brand by slug."""
    result = await session.execute(select(NutrientBrand).where(NutrientBrand.slug == slug))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.get("/lines", response_model=list[LineSummaryResponse])
async def list_lines(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_type: str | None = Query(None, description="Filter by compatible grow type slug"),
    line_type: str | None = Query(None, description="Filter by type: synthetic, organic, hybrid"),
    brand_slug: str | None = Query(None, description="Filter by brand slug"),
):
    """List nutrient lines, optionally filtered by grow type compatibility."""
    q = select(NutrientLine).options(selectinload(NutrientLine.brand))

    if grow_type:
        q = q.where(NutrientLine.grow_type_slugs.any(grow_type))
    if line_type:
        q = q.where(NutrientLine.line_type == line_type)
    if brand_slug:
        q = q.join(NutrientBrand).where(NutrientBrand.slug == brand_slug)

    q = q.order_by(NutrientLine.name)
    result = await session.execute(q)
    lines = result.scalars().all()
    return [
        LineSummaryResponse(
            id=line.id,
            slug=line.slug,
            name=line.name,
            description=line.description,
            line_type=line.line_type,
            part_count=line.part_count,
            format=line.format,
            difficulty=line.difficulty,
            ph_buffered=line.ph_buffered,
            grow_type_slugs=line.grow_type_slugs,
            brand_name=line.brand.name,
            brand_slug=line.brand.slug,
        )
        for line in lines
    ]


@router.get("/lines/{line_id}", response_model=LineResponse)
async def get_line(
    line_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a nutrient line with full details: products and feed chart."""
    result = await session.execute(
        select(NutrientLine)
        .where(NutrientLine.id == line_id)
        .options(
            selectinload(NutrientLine.brand),
            selectinload(NutrientLine.products),
            selectinload(NutrientLine.feed_charts),
        )
    )
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(status_code=404, detail="Nutrient line not found")
    return line


@router.get("/lines/{line_id}/feed-chart", response_model=list[FeedChartResponse])
async def get_feed_chart(
    line_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    stage: str | None = Query(None, description="Filter by stage: seedling, vegetative, flowering, flush"),
):
    """Get the week-by-week feed chart for a nutrient line."""
    q = select(NutrientFeedChart).where(NutrientFeedChart.line_id == line_id)
    if stage:
        q = q.where(NutrientFeedChart.stage == stage)
    q = q.order_by(NutrientFeedChart.week_number)
    result = await session.execute(q)
    return result.scalars().all()


# ═══════════════════════════════════════════════════════════════════════════════
# Additives Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/additives", response_model=list[AdditiveResponse])
async def list_additives(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_type: str | None = Query(None, description="Filter by compatible grow type slug"),
    category: str | None = Query(None, description="Filter by category: calmag, silica, enzyme, microbe, etc."),
):
    """List standalone additives, optionally filtered by grow type."""
    q = select(NutrientAdditive).options(selectinload(NutrientAdditive.brand))
    if grow_type:
        q = q.where(NutrientAdditive.grow_type_slugs.any(grow_type))
    if category:
        q = q.where(NutrientAdditive.category == category)
    q = q.order_by(NutrientAdditive.name)
    result = await session.execute(q)
    additives = result.scalars().all()
    return [
        AdditiveResponse(
            id=a.id,
            slug=a.slug,
            name=a.name,
            category=a.category,
            description=a.description,
            dose_ml_per_gallon=a.dose_ml_per_gallon,
            dose_grams_per_gallon=a.dose_grams_per_gallon,
            when_to_use=a.when_to_use,
            grow_type_slugs=a.grow_type_slugs,
            brand_name=a.brand.name if a.brand else None,
        )
        for a in additives
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Conflicts Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/conflicts", response_model=list[ConflictResponse])
async def list_conflicts(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """List all known nutrient conflicts."""
    result = await session.execute(select(NutrientConflict).order_by(NutrientConflict.severity.desc()))
    return result.scalars().all()


@router.post("/conflicts/check", response_model=list[ConflictResponse])
async def check_conflicts(
    items: list[str],
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Check a list of product/additive slugs for known conflicts."""
    if not items:
        return []
    result = await session.execute(select(NutrientConflict))
    all_conflicts = result.scalars().all()
    found = []
    item_set = set(items)
    for conflict in all_conflicts:
        if conflict.item_a_slug in item_set and conflict.item_b_slug in item_set:
            found.append(conflict)
    return found


# ═══════════════════════════════════════════════════════════════════════════════
# Organic Recipes Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/recipes", response_model=list[RecipeResponse])
async def list_recipes(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_type: str | None = Query(None, description="Filter by compatible grow type slug"),
    category: str | None = Query(None, description="Filter by category: compost_tea, dry_amendment, knf, etc."),
    stage: str | None = Query(None, description="Filter by best-for stage"),
):
    """List organic recipes, optionally filtered by grow type and category."""
    q = select(OrganicRecipe)
    if grow_type:
        q = q.where(OrganicRecipe.grow_type_slugs.any(grow_type))
    if category:
        q = q.where(OrganicRecipe.category == category)
    if stage:
        q = q.where(OrganicRecipe.best_for_stages.any(stage))
    q = q.order_by(OrganicRecipe.name)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/recipes/{slug}", response_model=RecipeResponse)
async def get_recipe(
    slug: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single organic recipe by slug."""
    result = await session.execute(select(OrganicRecipe).where(OrganicRecipe.slug == slug))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


# ═══════════════════════════════════════════════════════════════════════════════
# Custom Nutrients (tenant-scoped)
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/custom", response_model=list[CustomNutrientResponse])
async def list_custom_nutrients(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """List all custom nutrients for the current tenant."""
    result = await session.execute(
        select(CustomNutrient).where(CustomNutrient.tenant_id == user.tenant_id).order_by(CustomNutrient.name)
    )
    return result.scalars().all()


@router.post("/custom", response_model=CustomNutrientResponse, status_code=201)
async def create_custom_nutrient(
    body: CustomNutrientCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a custom nutrient (user-defined)."""
    nutrient = CustomNutrient(tenant_id=user.tenant_id, **body.model_dump())
    session.add(nutrient)
    await session.commit()
    await session.refresh(nutrient)
    return nutrient


@router.patch("/custom/{nutrient_id}", response_model=CustomNutrientResponse)
async def update_custom_nutrient(
    nutrient_id: UUID,
    body: CustomNutrientUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a custom nutrient."""
    nutrient = await session.get(CustomNutrient, nutrient_id)
    if not nutrient or nutrient.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Custom nutrient not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(nutrient, field, value)
    await session.commit()
    await session.refresh(nutrient)
    return nutrient


@router.delete("/custom/{nutrient_id}", status_code=204)
async def delete_custom_nutrient(
    nutrient_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a custom nutrient."""
    nutrient = await session.get(CustomNutrient, nutrient_id)
    if not nutrient or nutrient.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Custom nutrient not found")
    await session.delete(nutrient)
    await session.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# Grow Nutrient Profile (per-grow assignment)
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/profiles/{grow_cycle_id}", response_model=GrowNutrientProfileResponse | None)
async def get_grow_nutrient_profile(
    grow_cycle_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the nutrient profile for a grow cycle."""
    result = await session.execute(
        select(GrowNutrientProfile).where(
            GrowNutrientProfile.grow_cycle_id == grow_cycle_id,
            GrowNutrientProfile.tenant_id == user.tenant_id,
        )
    )
    return result.scalar_one_or_none()


@router.post("/profiles", response_model=GrowNutrientProfileResponse, status_code=201)
async def create_grow_nutrient_profile(
    body: GrowNutrientProfileCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create or update the nutrient profile for a grow cycle."""
    # Check if profile already exists
    existing = await session.execute(
        select(GrowNutrientProfile).where(GrowNutrientProfile.grow_cycle_id == body.grow_cycle_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Nutrient profile already exists for this grow. Use PATCH to update."
        )

    profile = GrowNutrientProfile(tenant_id=user.tenant_id, **body.model_dump())
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.patch("/profiles/{grow_cycle_id}", response_model=GrowNutrientProfileResponse)
async def update_grow_nutrient_profile(
    grow_cycle_id: UUID,
    body: GrowNutrientProfileUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update the nutrient profile for a grow cycle."""
    result = await session.execute(
        select(GrowNutrientProfile).where(
            GrowNutrientProfile.grow_cycle_id == grow_cycle_id,
            GrowNutrientProfile.tenant_id == user.tenant_id,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Nutrient profile not found for this grow")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.delete("/profiles/{grow_cycle_id}", status_code=204)
async def delete_grow_nutrient_profile(
    grow_cycle_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete the nutrient profile for a grow cycle."""
    result = await session.execute(
        select(GrowNutrientProfile).where(
            GrowNutrientProfile.grow_cycle_id == grow_cycle_id,
            GrowNutrientProfile.tenant_id == user.tenant_id,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Nutrient profile not found")
    await session.delete(profile)
    await session.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# Feeding Recommendation (computed from profile + current week)
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/recommend/{grow_cycle_id}", response_model=FeedingRecommendationResponse)
async def get_feeding_recommendation(
    grow_cycle_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    week: int = Query(..., ge=1, le=20, description="Current grow week number"),
):
    """Get the computed feeding recommendation for a specific week based on the grow's nutrient profile."""
    from app.nutrition.service import compute_recommendation

    result = await session.execute(
        select(GrowNutrientProfile).where(
            GrowNutrientProfile.grow_cycle_id == grow_cycle_id,
            GrowNutrientProfile.tenant_id == user.tenant_id,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="No nutrient profile configured for this grow")

    recommendation = await compute_recommendation(session, profile, week)
    return recommendation
