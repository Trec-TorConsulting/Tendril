"""Reference data domain service.

Holds the business operations for the reference catalogues
(strains, nutrient products, feed charts, ESPHome templates,
nutrient knowledge base) and the strain-sync admin op.

Route handlers in ``app.reference.routes`` are HTTP-only and delegate
to this module.

Conventions match the project standard (PR #192 / #208-#215):

* The first positional argument is always ``session: AsyncSession``.
* Functions return ORM model instances, dataclasses, or primitives;
  they never raise ``HTTPException`` — lookup misses return ``None``.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sqlalchemy import distinct, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import NutrientProduct, ReferenceStrain
from app.reference.models import ESPHomeTemplate, FeedChart, NutrientKnowledge

# ─────────────────────────────────────────────────────────────────────────────
# Reference strains
# ─────────────────────────────────────────────────────────────────────────────


async def search_reference_strains(session: AsyncSession, *, query: str, limit: int) -> list[ReferenceStrain]:
    """Case-insensitive substring autocomplete on strain name."""
    result = await session.execute(
        select(ReferenceStrain)
        .where(ReferenceStrain.name.ilike(f"%{query}%"))
        .order_by(ReferenceStrain.name)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_reference_strain(session: AsyncSession, strain_id: UUID) -> ReferenceStrain | None:
    return await session.get(ReferenceStrain, strain_id)


# ─────────────────────────────────────────────────────────────────────────────
# Nutrient products
# ─────────────────────────────────────────────────────────────────────────────


async def get_nutrient_product_by_barcode(session: AsyncSession, barcode: str) -> NutrientProduct | None:
    return (
        await session.execute(select(NutrientProduct).where(NutrientProduct.barcode == barcode))
    ).scalar_one_or_none()


async def search_nutrient_products(session: AsyncSession, *, query: str, limit: int) -> list[NutrientProduct]:
    """Case-insensitive substring search across product name *and* brand."""
    result = await session.execute(
        select(NutrientProduct)
        .where(
            or_(
                NutrientProduct.name.ilike(f"%{query}%"),
                NutrientProduct.brand.ilike(f"%{query}%"),
            )
        )
        .order_by(NutrientProduct.name)
        .limit(limit)
    )
    return list(result.scalars().all())


# ─────────────────────────────────────────────────────────────────────────────
# Feed charts
# ─────────────────────────────────────────────────────────────────────────────


async def list_feed_charts(session: AsyncSession, *, brand: str | None) -> list[FeedChart]:
    """All feed charts, optionally filtered by brand (case-insensitive equality
    via ILIKE — matches previous route behaviour)."""
    query = select(FeedChart)
    if brand:
        query = query.where(FeedChart.brand.ilike(brand))
    return list((await session.execute(query)).scalars().all())


def filter_feed_charts_by_medium(charts: Iterable[FeedChart], medium: str | None) -> list[FeedChart]:
    """Filter feed charts down to those whose ``medium`` list contains ``medium``.

    Kept in the service (rather than as a DB filter) because ``medium`` is a
    JSON list column and the previous route did a Python-side check.
    """
    if not medium:
        return list(charts)
    needle = medium.lower()
    return [c for c in charts if needle in (c.medium or [])]


async def list_feed_chart_brands(session: AsyncSession) -> list[str]:
    """Distinct brand names, alphabetically ordered."""
    result = await session.execute(select(distinct(FeedChart.brand)).order_by(FeedChart.brand))
    return [row[0] for row in result.all()]


# ─────────────────────────────────────────────────────────────────────────────
# ESPHome templates
# ─────────────────────────────────────────────────────────────────────────────


async def list_esphome_templates(session: AsyncSession) -> list[ESPHomeTemplate]:
    return list((await session.execute(select(ESPHomeTemplate))).scalars().all())


async def get_esphome_template_by_template_id(session: AsyncSession, template_id: str) -> ESPHomeTemplate | None:
    return (
        await session.execute(select(ESPHomeTemplate).where(ESPHomeTemplate.template_id == template_id))
    ).scalar_one_or_none()


def slugify_device_name(name: str) -> str:
    """Lowercase + replace spaces/underscores with hyphens.

    Matches the previous private formatting in
    ``generate_esphome_config``.
    """
    return name.lower().replace(" ", "-").replace("_", "-")


def render_esphome_yaml(
    template: ESPHomeTemplate,
    *,
    device_name: str,
    mqtt_host: str,
    mqtt_user: str,
    mqtt_password: str,
    wifi_ssid: str,
    wifi_password: str,
) -> str:
    """Render an ESPHome YAML config from ``template`` + user-supplied
    secrets. Pure function — no I/O — so tests can assert the YAML shape
    without spinning up a DB session.
    """
    device_slug = slugify_device_name(device_name)
    return f"""# ESPHome config generated by Tendril
# Template: {template.name}
# Sensors: {", ".join(template.sensors)}

esphome:
  name: {device_slug}
  friendly_name: "{device_name}"

esp32:
  board: {template.board}

wifi:
  ssid: "{wifi_ssid}"
  password: "{wifi_password}"
  ap:
    ssid: "{device_name} Fallback"
    password: "tendril-setup"

mqtt:
  broker: "{mqtt_host}"
  username: "{mqtt_user}"
  password: "{mqtt_password}"
  topic_prefix: "tendril/{device_slug}"
  discovery: false

logger:
  level: INFO

ota:
  platform: esphome
{template.yaml_body}"""


# ─────────────────────────────────────────────────────────────────────────────
# Strain sync (admin op)
# ─────────────────────────────────────────────────────────────────────────────


async def sync_seed_reference_strains(session: AsyncSession) -> int:
    """Thin wrapper around the existing seed-strain sync routine.

    Kept here so the route layer has one consistent service surface and
    so future expansion (sync from external API, etc.) has a natural
    home.
    """
    from app.reference.strain_sync import sync_seed_strains

    return await sync_seed_strains(session)


# ─────────────────────────────────────────────────────────────────────────────
# Nutrient knowledge base
# ─────────────────────────────────────────────────────────────────────────────


# Single source of truth — the four categories the public API surfaces.
NUTRIENT_KNOWLEDGE_CATEGORIES = (
    "diy_recipe",
    "emergency_substitution",
    "ph_alternative",
    "methodology_guide",
)


async def list_nutrient_knowledge_entries(
    session: AsyncSession, *, category: str | None = None
) -> list[NutrientKnowledge]:
    """All knowledge entries, optionally filtered by category."""
    query = select(NutrientKnowledge)
    if category:
        query = query.where(NutrientKnowledge.category == category)
    return list((await session.execute(query)).scalars().all())


async def get_nutrient_knowledge_grouped(
    session: AsyncSession,
) -> dict[str, list[Any]]:
    """Return all knowledge entries grouped by category. Each value is the
    list of ``data`` payloads for that category (ORM ``data`` column)."""
    entries = await list_nutrient_knowledge_entries(session)
    grouped: dict[str, list[Any]] = {}
    for e in entries:
        grouped.setdefault(e.category, []).append(e.data)
    return grouped


# ── Pure filters (testable without a DB) ─────────────────────────────────────


def filter_diy_recipes(
    recipes: Iterable[dict],
    *,
    category: str | None,
    difficulty: str | None,
) -> list[dict]:
    """Pure helper — narrow a list of DIY recipe payloads."""
    out = list(recipes)
    if category:
        out = [r for r in out if r.get("category") == category]
    if difficulty:
        out = [r for r in out if r.get("difficulty") == difficulty]
    return out


def filter_emergency_substitutions(subs: Iterable[dict], *, deficiency: str | None) -> list[dict]:
    """Pure helper — case-insensitive substring match on the ``id`` field."""
    if not deficiency:
        return list(subs)
    needle = deficiency.lower()
    return [s for s in subs if needle in s.get("id", "")]


def filter_ph_alternatives(alts: Iterable[dict], *, direction: str | None) -> list[dict]:
    """Pure helper — case-insensitive equality on ``direction``."""
    if not direction:
        return list(alts)
    needle = direction.lower()
    return [a for a in alts if a.get("direction") == needle]


def filter_methodology_guides(guides: Iterable[dict], *, approach: str | None) -> list[dict]:
    """Pure helper — case-insensitive equality on ``approach``."""
    if not approach:
        return list(guides)
    needle = approach.lower()
    return [g for g in guides if g.get("approach") == needle]


async def list_diy_recipes(session: AsyncSession, *, category: str | None, difficulty: str | None) -> list[dict]:
    entries = await list_nutrient_knowledge_entries(session, category="diy_recipe")
    return filter_diy_recipes((e.data for e in entries), category=category, difficulty=difficulty)


async def list_emergency_substitutions(session: AsyncSession, *, deficiency: str | None) -> list[dict]:
    entries = await list_nutrient_knowledge_entries(session, category="emergency_substitution")
    return filter_emergency_substitutions((e.data for e in entries), deficiency=deficiency)


async def list_ph_alternatives(session: AsyncSession, *, direction: str | None) -> list[dict]:
    entries = await list_nutrient_knowledge_entries(session, category="ph_alternative")
    return filter_ph_alternatives((e.data for e in entries), direction=direction)


async def list_methodology_guides(session: AsyncSession, *, approach: str | None) -> list[dict]:
    entries = await list_nutrient_knowledge_entries(session, category="methodology_guide")
    return filter_methodology_guides((e.data for e in entries), approach=approach)
