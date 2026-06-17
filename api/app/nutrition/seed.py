"""Nutrition seed sync — loads all brand, line, product, chart, additive, conflict, and recipe data into DB."""

from __future__ import annotations

import logging
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.nutrition import (
    NutrientAdditive,
    NutrientBrand,
    NutrientConflict,
    NutrientFeedChart,
    NutrientLine,
    NutrientLineProduct,
    OrganicRecipe,
)
from app.nutrition.seed_additives import ADDITIVES, CONFLICTS
from app.nutrition.seed_brands import BRANDS, HYDRO_LINES
from app.nutrition.seed_charts import FEED_CHARTS
from app.nutrition.seed_lines import COCO_LINES, ORGANIC_LINES, SOIL_LINES
from app.nutrition.seed_recipes import ORGANIC_RECIPES

logger = logging.getLogger("tendril.nutrition.seed")


async def sync_nutrition_seed(session: AsyncSession) -> None:
    """Seed or update all nutrition reference data. Idempotent — uses slug-based upsert."""
    await _sync_brands(session)
    await _sync_lines(session, HYDRO_LINES + COCO_LINES + SOIL_LINES + ORGANIC_LINES)
    await _sync_feed_charts(session)
    await _sync_additives(session)
    await _sync_conflicts(session)
    await _sync_recipes(session)
    await session.commit()
    logger.info("Nutrition seed data sync complete")


async def _sync_brands(session: AsyncSession) -> None:
    """Upsert brands by slug."""
    for brand_data in BRANDS:
        result = await session.execute(select(NutrientBrand).where(NutrientBrand.slug == brand_data["slug"]))
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in brand_data.items():
                setattr(existing, key, value)
        else:
            session.add(NutrientBrand(**brand_data))
    await session.flush()


async def _sync_lines(session: AsyncSession, all_lines: list[dict]) -> None:
    """Upsert lines and their products by brand_slug + line_slug."""
    for line_data in all_lines:
        brand_slug = line_data.pop("brand_slug")
        products_data = line_data.pop("products", [])

        # Look up brand
        brand_result = await session.execute(select(NutrientBrand).where(NutrientBrand.slug == brand_slug))
        brand = brand_result.scalar_one_or_none()
        if not brand:
            logger.warning("Brand %s not found, skipping line %s", brand_slug, line_data["slug"])
            line_data["brand_slug"] = brand_slug
            line_data["products"] = products_data
            continue

        # Upsert line
        line_result = await session.execute(
            select(NutrientLine).where(
                NutrientLine.brand_id == brand.id,
                NutrientLine.slug == line_data["slug"],
            )
        )
        existing_line = line_result.scalar_one_or_none()
        line: NutrientLine
        if existing_line:
            for key, value in line_data.items():
                setattr(existing_line, key, value)
            line = existing_line
        else:
            line = NutrientLine(brand_id=brand.id, **line_data)
            session.add(line)
            await session.flush()

        # Upsert products
        for product_data in products_data:
            result = await session.execute(
                select(NutrientLineProduct).where(
                    NutrientLineProduct.line_id == line.id,
                    NutrientLineProduct.slug == product_data["slug"],
                )
            )
            existing_product = result.scalar_one_or_none()
            if existing_product:
                for key, value in product_data.items():
                    setattr(existing_product, key, value)
            else:
                session.add(NutrientLineProduct(line_id=line.id, **product_data))

        # Restore popped keys for potential re-use
        line_data["brand_slug"] = brand_slug
        line_data["products"] = products_data

    await session.flush()


async def _sync_feed_charts(session: AsyncSession) -> None:
    """Upsert feed charts by line_slug + week_number."""
    for line_slug, chart_data in FEED_CHARTS.items():
        # Find line by slug (across all brands)
        result = await session.execute(select(NutrientLine).where(NutrientLine.slug == line_slug))
        line = result.scalar_one_or_none()
        if not line:
            logger.warning("Line %s not found for feed chart, skipping", line_slug)
            continue

        for week_data in chart_data:
            week_payload = cast(dict[str, Any], week_data)
            result = await session.execute(
                select(NutrientFeedChart).where(
                    NutrientFeedChart.line_id == line.id,
                    NutrientFeedChart.week_number == cast(int, week_payload["week_number"]),
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in week_payload.items():
                    setattr(existing, key, value)
            else:
                session.add(NutrientFeedChart(line_id=line.id, **week_payload))

    await session.flush()


async def _sync_additives(session: AsyncSession) -> None:
    """Upsert additives by brand_slug + additive_slug."""
    for additive_data in ADDITIVES:
        brand_slug = additive_data.pop("brand_slug")

        result = await session.execute(select(NutrientBrand).where(NutrientBrand.slug == brand_slug))
        brand = result.scalar_one_or_none()
        if not brand:
            logger.warning("Brand %s not found for additive %s", brand_slug, additive_data.get("slug"))
            additive_data["brand_slug"] = brand_slug
            continue

        result = await session.execute(
            select(NutrientAdditive).where(
                NutrientAdditive.brand_id == brand.id,
                NutrientAdditive.slug == additive_data["slug"],
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in additive_data.items():
                setattr(existing, key, value)
        else:
            session.add(NutrientAdditive(brand_id=brand.id, **additive_data))

        additive_data["brand_slug"] = brand_slug

    await session.flush()


async def _sync_conflicts(session: AsyncSession) -> None:
    """Upsert conflicts by item_a_slug + item_b_slug."""
    for conflict_data in CONFLICTS:
        result = await session.execute(
            select(NutrientConflict).where(
                NutrientConflict.item_a_slug == conflict_data["item_a_slug"],
                NutrientConflict.item_b_slug == conflict_data["item_b_slug"],
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in conflict_data.items():
                setattr(existing, key, value)
        else:
            session.add(NutrientConflict(**conflict_data))

    await session.flush()


async def _sync_recipes(session: AsyncSession) -> None:
    """Upsert organic recipes by slug."""
    for recipe_data in ORGANIC_RECIPES:
        recipe_payload = cast(dict[str, Any], recipe_data)
        result = await session.execute(select(OrganicRecipe).where(OrganicRecipe.slug == cast(str, recipe_payload["slug"])))
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in recipe_payload.items():
                setattr(existing, key, value)
        else:
            session.add(OrganicRecipe(**recipe_payload))

    await session.flush()
