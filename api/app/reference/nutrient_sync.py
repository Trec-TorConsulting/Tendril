"""Nutrient product database sync — imports seed data for common nutrient products."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import NutrientProduct

logger = logging.getLogger("tendril.reference.nutrients")

# Curated seed data for popular nutrient products
SEED_NUTRIENTS: list[dict] = [
    {
        "barcode": "0849953000018",
        "name": "Micro",
        "brand": "General Hydroponics Flora",
        "npk": "5-0-1",
        "source": "seed",
    },
    {
        "barcode": "0849953000025",
        "name": "Gro",
        "brand": "General Hydroponics Flora",
        "npk": "2-1-6",
        "source": "seed",
    },
    {
        "barcode": "0849953000032",
        "name": "Bloom",
        "brand": "General Hydroponics Flora",
        "npk": "0-5-4",
        "source": "seed",
    },
    {
        "barcode": "0849953000100",
        "name": "CALiMAGic",
        "brand": "General Hydroponics",
        "npk": "1-0-0",
        "source": "seed",
    },
    {
        "barcode": "0793094014809",
        "name": "Big Bloom",
        "brand": "Fox Farm",
        "npk": "0.01-0.3-0.7",
        "source": "seed",
    },
    {
        "barcode": "0793094014816",
        "name": "Grow Big",
        "brand": "Fox Farm",
        "npk": "6-4-4",
        "source": "seed",
    },
    {
        "barcode": "0793094014823",
        "name": "Tiger Bloom",
        "brand": "Fox Farm",
        "npk": "2-8-4",
        "source": "seed",
    },
    {
        "barcode": "0AN100001001",
        "name": "pH Perfect Micro",
        "brand": "Advanced Nutrients",
        "npk": "5-0-1",
        "source": "seed",
    },
    {
        "barcode": "0AN100001002",
        "name": "pH Perfect Grow",
        "brand": "Advanced Nutrients",
        "npk": "1-3-6",
        "source": "seed",
    },
    {
        "barcode": "0AN100001003",
        "name": "pH Perfect Bloom",
        "brand": "Advanced Nutrients",
        "npk": "0-5-4",
        "source": "seed",
    },
    {
        "barcode": "0AN100001010",
        "name": "Big Bud",
        "brand": "Advanced Nutrients",
        "npk": "0-1-3",
        "source": "seed",
    },
    {
        "barcode": "0AN100001020",
        "name": "Overdrive",
        "brand": "Advanced Nutrients",
        "npk": "1-5-4",
        "source": "seed",
    },
    {
        "barcode": "0JN321010001",
        "name": "Jack's 3-2-1 Part A",
        "brand": "Jack's Nutrients",
        "npk": "5-12-26",
        "source": "seed",
    },
    {
        "barcode": "0JN321010002",
        "name": "Calcium Nitrate",
        "brand": "Jack's Nutrients",
        "npk": "15.5-0-0",
        "source": "seed",
    },
    {
        "barcode": "0JN321010003",
        "name": "Epsom Salt (Magnesium Sulfate)",
        "brand": "Jack's Nutrients",
        "npk": "0-0-0",
        "source": "seed",
    },
    {
        "barcode": "0CR100001001",
        "name": "Canna A",
        "brand": "Canna Coco",
        "npk": "5-0-3",
        "source": "seed",
    },
    {
        "barcode": "0CR100001002",
        "name": "Canna B",
        "brand": "Canna Coco",
        "npk": "1-4-2",
        "source": "seed",
    },
    {
        "barcode": "0CR100001010",
        "name": "PK 13/14",
        "brand": "Canna",
        "npk": "0-13-14",
        "source": "seed",
    },
    {
        "barcode": "0CR100001020",
        "name": "Cannazym",
        "brand": "Canna",
        "npk": "0-0-0",
        "source": "seed",
    },
    {
        "barcode": "0AM100001001",
        "name": "Sensi Grow A",
        "brand": "Advanced Nutrients Sensi",
        "npk": "5-0-1",
        "source": "seed",
    },
    {
        "barcode": "0AM100001002",
        "name": "Sensi Grow B",
        "brand": "Advanced Nutrients Sensi",
        "npk": "1-2-6",
        "source": "seed",
    },
    {
        "barcode": "0AM100001003",
        "name": "Sensi Bloom A",
        "brand": "Advanced Nutrients Sensi",
        "npk": "4-0-3",
        "source": "seed",
    },
    {
        "barcode": "0AM100001004",
        "name": "Sensi Bloom B",
        "brand": "Advanced Nutrients Sensi",
        "npk": "0-4-3",
        "source": "seed",
    },
    {
        "barcode": "0BN100001001",
        "name": "Veg+Bloom Dirty",
        "brand": "Veg+Bloom",
        "npk": "9-13-27",
        "source": "seed",
    },
    {
        "barcode": "0BN100001002",
        "name": "Veg+Bloom RO/Soft",
        "brand": "Veg+Bloom",
        "npk": "11-14-27",
        "source": "seed",
    },
    {
        "barcode": "0MG100001001",
        "name": "Armor Si",
        "brand": "General Hydroponics",
        "npk": "0-0-0",
        "source": "seed",
    },
    {
        "barcode": "0MG100001002",
        "name": "Hydroguard",
        "brand": "Botanicare",
        "npk": "0-0-0",
        "source": "seed",
    },
    {
        "barcode": "0MG100001003",
        "name": "Recharge",
        "brand": "Real Growers",
        "npk": "0-0-0",
        "source": "seed",
    },
    {
        "barcode": "0MG100001004",
        "name": "Mammoth P",
        "brand": "Mammoth Microbes",
        "npk": "0-0-0",
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0001",
        "name": "Core",
        "brand": "Athena",
        "npk": "5-0-0",
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0002",
        "name": "Grow A",
        "brand": "Athena",
        "npk": "4-0-1",
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0003",
        "name": "Grow B",
        "brand": "Athena",
        "npk": "1-3-5",
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0004",
        "name": "Bloom A",
        "brand": "Athena",
        "npk": "4-0-1",
        "source": "seed",
    },
    {
        "barcode": "0ATHENA0005",
        "name": "Bloom B",
        "brand": "Athena",
        "npk": "1-4-5",
        "source": "seed",
    },
]


async def sync_seed_nutrients(session: AsyncSession) -> int:
    """Seed the nutrient_products table with curated data. Returns count of new nutrients added."""
    added = 0
    for nutrient_data in SEED_NUTRIENTS:
        existing = (
            await session.execute(select(NutrientProduct).where(NutrientProduct.barcode == nutrient_data["barcode"]))
        ).scalar_one_or_none()

        if existing:
            for key, value in nutrient_data.items():
                setattr(existing, key, value)
            existing.synced_at = datetime.now(UTC)
        else:
            product = NutrientProduct(
                **nutrient_data,
                synced_at=datetime.now(UTC),
            )
            session.add(product)
            added += 1

    await session.commit()
    logger.info("Nutrient sync complete: %d new, %d total", added, len(SEED_NUTRIENTS))
    return added
