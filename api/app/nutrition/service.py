"""Nutrition service — recommendation engine, conflict checking, profile computation."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.nutrition import (
    CustomNutrient,
    GrowNutrientProfile,
    NutrientAdditive,
    NutrientConflict,
    NutrientFeedChart,
    NutrientLine,
    NutrientProduct,
    OrganicRecipe,
)


async def compute_recommendation(
    session: AsyncSession,
    profile: GrowNutrientProfile,
    week: int,
) -> dict:
    """Compute the full feeding recommendation for a given week based on the user's nutrient profile."""

    primary_doses: list[dict] = []
    secondary_doses: list[dict] = []
    additive_info: list[dict] = []
    recipe_info: list[dict] = []
    custom_info: list[dict] = []
    target_ec_min = None
    target_ec_max = None
    target_ph_min = None
    target_ph_max = None
    stage = "vegetative"
    phase_name = f"Week {week}"
    notes = None
    strength_mult = (profile.strength_pct or 100) / 100.0

    # Primary line feed chart
    if profile.primary_line_id:
        chart = await _get_chart_for_week(session, profile.primary_line_id, week)
        if chart:
            stage = chart.stage
            phase_name = chart.phase_name
            target_ec_min = chart.target_ec_min
            target_ec_max = chart.target_ec_max
            target_ph_min = chart.target_ph_min
            target_ph_max = chart.target_ph_max
            notes = chart.notes
            primary_doses = _apply_strength(chart.doses, strength_mult, profile.selected_products)

    # Secondary line feed chart (mix and match)
    if profile.secondary_line_id:
        chart = await _get_chart_for_week(session, profile.secondary_line_id, week)
        if chart:
            secondary_doses = _apply_strength(chart.doses, strength_mult, profile.selected_products)

    # Selected additives
    if profile.selected_additives:
        result = await session.execute(
            select(NutrientAdditive).where(NutrientAdditive.slug.in_(profile.selected_additives))
        )
        for additive in result.scalars().all():
            additive_info.append({
                "slug": additive.slug,
                "name": additive.name,
                "category": additive.category,
                "dose_ml_per_gallon": additive.dose_ml_per_gallon,
                "dose_grams_per_gallon": additive.dose_grams_per_gallon,
                "when_to_use": additive.when_to_use,
            })

    # Selected recipes
    if profile.selected_recipes:
        result = await session.execute(
            select(OrganicRecipe).where(OrganicRecipe.slug.in_(profile.selected_recipes))
        )
        for recipe in result.scalars().all():
            # Only include if recipe is appropriate for current stage
            if recipe.best_for_stages and stage not in recipe.best_for_stages:
                continue
            recipe_info.append({
                "slug": recipe.slug,
                "name": recipe.name,
                "category": recipe.category,
                "application_rate": recipe.application_rate,
                "frequency": recipe.frequency,
            })

    # Custom nutrients
    if profile.custom_nutrient_ids:
        result = await session.execute(
            select(CustomNutrient).where(CustomNutrient.id.in_(profile.custom_nutrient_ids))
        )
        for custom in result.scalars().all():
            custom_info.append({
                "id": str(custom.id),
                "name": custom.name,
                "nutrient_type": custom.nutrient_type,
                "dose_ml_per_gallon": custom.dose_ml_per_gallon,
                "dose_grams_per_gallon": custom.dose_grams_per_gallon,
            })

    # Check for conflicts
    all_slugs = []
    for d in primary_doses + secondary_doses:
        all_slugs.append(d.get("product_slug", ""))
    if profile.selected_additives:
        all_slugs.extend(profile.selected_additives)
    conflicts = await _check_conflicts(session, all_slugs)

    return {
        "week_number": week,
        "stage": stage,
        "phase_name": phase_name,
        "primary_line_doses": primary_doses,
        "secondary_line_doses": secondary_doses,
        "additives": additive_info,
        "recipes": recipe_info,
        "custom_nutrients": custom_info,
        "target_ec_min": target_ec_min,
        "target_ec_max": target_ec_max,
        "target_ph_min": target_ph_min,
        "target_ph_max": target_ph_max,
        "conflicts": conflicts,
        "notes": notes,
    }


async def _get_chart_for_week(session: AsyncSession, line_id, week: int) -> NutrientFeedChart | None:
    """Get the feed chart entry for a specific week, or the closest available."""
    result = await session.execute(
        select(NutrientFeedChart)
        .where(NutrientFeedChart.line_id == line_id, NutrientFeedChart.week_number == week)
    )
    chart = result.scalar_one_or_none()
    if chart:
        return chart

    # Fall back to the closest week (last available if past end of chart)
    result = await session.execute(
        select(NutrientFeedChart)
        .where(NutrientFeedChart.line_id == line_id)
        .order_by(NutrientFeedChart.week_number.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _apply_strength(doses: list[dict], strength_mult: float, selected_products: list[str] | None) -> list[dict]:
    """Apply strength multiplier and filter to selected products."""
    result = []
    for dose in doses:
        slug = dose.get("product_slug", "")
        # If user has selected specific products, only include those
        if selected_products and slug not in selected_products:
            continue
        adjusted = dict(dose)
        if "ml_per_gallon" in adjusted and adjusted["ml_per_gallon"]:
            adjusted["ml_per_gallon"] = round(adjusted["ml_per_gallon"] * strength_mult, 2)
        if "grams_per_gallon" in adjusted and adjusted["grams_per_gallon"]:
            adjusted["grams_per_gallon"] = round(adjusted["grams_per_gallon"] * strength_mult, 3)
        result.append(adjusted)
    return result


async def _check_conflicts(session: AsyncSession, slugs: list[str]) -> list[dict]:
    """Check for known conflicts among a list of product/additive slugs."""
    if not slugs:
        return []
    slug_set = set(s for s in slugs if s)
    result = await session.execute(select(NutrientConflict))
    conflicts = result.scalars().all()
    found = []
    for c in conflicts:
        if c.item_a_slug in slug_set and c.item_b_slug in slug_set:
            found.append({
                "id": str(c.id),
                "item_a_type": c.item_a_type,
                "item_a_slug": c.item_a_slug,
                "item_b_type": c.item_b_type,
                "item_b_slug": c.item_b_slug,
                "severity": c.severity,
                "reason": c.reason,
                "recommendation": c.recommendation,
            })
    return found
