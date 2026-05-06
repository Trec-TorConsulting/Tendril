"""Strain database sync — imports reference strains from external API or seed data."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import ReferenceStrain

logger = logging.getLogger("tendril.reference.strains")

# Curated seed data for common strains (avoids dependency on external API availability)
SEED_STRAINS: list[dict] = [
    {
        "name": "Blue Dream",
        "breeder": "DJ Short / Santa Cruz",
        "genetics": "Blueberry x Haze",
        "thc_pct": 21.0,
        "cbd_pct": 0.1,
        "description": "Sativa-dominant hybrid. Sweet berry aroma, balanced cerebral and body effects.",
    },
    {
        "name": "Girl Scout Cookies",
        "breeder": "Cookie Family",
        "genetics": "OG Kush x Durban Poison",
        "thc_pct": 25.0,
        "cbd_pct": 0.2,
        "description": "Hybrid. Sweet, earthy, pungent. Strong euphoria with full-body relaxation.",
    },
    {
        "name": "OG Kush",
        "breeder": "Unknown (FL origin)",
        "genetics": "Chemdawg x Hindu Kush x Lemon Thai",
        "thc_pct": 23.0,
        "cbd_pct": 0.3,
        "description": "Indica-dominant hybrid. Fuel, skunk, spice. Heavy euphoria, stress relief.",
    },
    {
        "name": "Gorilla Glue #4",
        "breeder": "GG Strains",
        "genetics": "Chem's Sister x Sour Dubb x Chocolate Diesel",
        "thc_pct": 28.0,
        "cbd_pct": 0.1,
        "description": "Hybrid. Pine, chocolate, diesel. Extremely potent, couch-lock.",
    },
    {
        "name": "Gelato",
        "breeder": "Cookie Family",
        "genetics": "Sunset Sherbet x Thin Mint GSC",
        "thc_pct": 25.0,
        "cbd_pct": 0.1,
        "description": "Hybrid. Sweet, citrus, lavender. Balanced relaxation with mental stimulation.",
    },
    {
        "name": "Wedding Cake",
        "breeder": "Seed Junky Genetics",
        "genetics": "Triangle Kush x Animal Mints",
        "thc_pct": 25.0,
        "cbd_pct": 0.1,
        "description": "Indica-dominant. Sweet, tangy, earthy. Relaxing, euphoric.",
    },
    {
        "name": "Jack Herer",
        "breeder": "Sensi Seeds",
        "genetics": "Haze x Northern Lights #5 x Shiva Skunk",
        "thc_pct": 20.0,
        "cbd_pct": 0.1,
        "description": "Sativa-dominant. Pine, spice, floral. Creative, blissful, clear-headed.",
    },
    {
        "name": "Northern Lights",
        "breeder": "Sensi Seeds",
        "genetics": "Afghani Landrace",
        "thc_pct": 18.0,
        "cbd_pct": 0.1,
        "description": "Pure indica. Sweet, spicy, earthy. Heavy body stone, pain relief. Easy to grow.",
    },
    {
        "name": "Sour Diesel",
        "breeder": "Unknown (East Coast)",
        "genetics": "Chemdawg 91 x Super Skunk",
        "thc_pct": 22.0,
        "cbd_pct": 0.2,
        "description": "Sativa-dominant. Diesel, citrus. Energizing, dreamy cerebral effects.",
    },
    {
        "name": "White Widow",
        "breeder": "Green House Seeds",
        "genetics": "Brazilian Sativa x South Indian Indica",
        "thc_pct": 20.0,
        "cbd_pct": 0.2,
        "description": "Balanced hybrid. Earthy, woody, pungent. Powerful euphoria with creativity.",
    },
    {
        "name": "AK-47",
        "breeder": "Serious Seeds",
        "genetics": "Colombian x Mexican x Thai x Afghani",
        "thc_pct": 20.0,
        "cbd_pct": 0.1,
        "description": "Sativa-dominant. Earthy, floral, sweet. Long-lasting cerebral buzz.",
    },
    {
        "name": "Purple Punch",
        "breeder": "Supernova Gardens",
        "genetics": "Larry OG x Granddaddy Purple",
        "thc_pct": 20.0,
        "cbd_pct": 0.1,
        "description": "Indica-dominant. Grape, blueberry, vanilla. Sedating, pain relief.",
    },
    {
        "name": "Zkittlez",
        "breeder": "3rd Gen Family / Terp Hogz",
        "genetics": "Grape Ape x Grapefruit",
        "thc_pct": 23.0,
        "cbd_pct": 0.1,
        "description": "Indica-dominant. Sweet, tropical, berry. Calming, happy, focused.",
    },
    {
        "name": "Runtz",
        "breeder": "Cookies",
        "genetics": "Zkittlez x Gelato",
        "thc_pct": 24.0,
        "cbd_pct": 0.1,
        "description": "Hybrid. Sweet candy, fruity, creamy. Euphoric, giggly, relaxing.",
    },
    {
        "name": "Mimosa",
        "breeder": "Symbiotic Genetics",
        "genetics": "Clementine x Purple Punch",
        "thc_pct": 22.0,
        "cbd_pct": 0.1,
        "description": "Sativa-dominant. Citrus, tropical, sweet. Uplifting, energetic, focused.",
    },
    {
        "name": "Do-Si-Dos",
        "breeder": "Archive Seed Bank",
        "genetics": "Girl Scout Cookies x Face Off OG",
        "thc_pct": 26.0,
        "cbd_pct": 0.1,
        "description": "Indica-dominant. Earthy, sweet, floral. Powerful body relaxation.",
    },
    {
        "name": "Granddaddy Purple",
        "breeder": "Ken Estes",
        "genetics": "Purple Urkle x Big Bud",
        "thc_pct": 20.0,
        "cbd_pct": 0.1,
        "description": "Pure indica. Grape, berry, sweet. Full-body relaxation, sleepy.",
    },
    {
        "name": "Green Crack",
        "breeder": "Cecil C.",
        "genetics": "Skunk #1 x Isolated Afghani Cut",
        "thc_pct": 21.0,
        "cbd_pct": 0.1,
        "description": "Sativa-dominant. Mango, citrus, sweet. Sharp energy, mental focus.",
    },
    {
        "name": "Bruce Banner",
        "breeder": "Dark Horse Genetics",
        "genetics": "OG Kush x Strawberry Diesel",
        "thc_pct": 29.0,
        "cbd_pct": 0.1,
        "description": "Hybrid. Diesel, sweet, earthy. Extremely potent, euphoric, creative.",
    },
    {
        "name": "MAC (Miracle Alien Cookies)",
        "breeder": "Capulator",
        "genetics": "Alien Cookies x Colombian x Starfighter",
        "thc_pct": 23.0,
        "cbd_pct": 0.1,
        "description": "Hybrid. Citrus, floral, dough. Creative, happy, uplifting.",
    },
]


async def sync_seed_strains(session: AsyncSession) -> int:
    """Seed the reference_strains table with curated data. Returns count of new strains added."""
    added = 0
    for strain_data in SEED_STRAINS:
        existing = (
            await session.execute(select(ReferenceStrain).where(ReferenceStrain.name == strain_data["name"]))
        ).scalar_one_or_none()

        if existing:
            # Update existing record
            for key, value in strain_data.items():
                setattr(existing, key, value)
            existing.synced_at = datetime.now(UTC)
        else:
            strain = ReferenceStrain(
                **strain_data,
                external_id=f"seed:{strain_data['name'].lower().replace(' ', '-')}",
                synced_at=datetime.now(UTC),
            )
            session.add(strain)
            added += 1

    await session.commit()
    logger.info("Strain sync complete: %d new, %d total", added, len(SEED_STRAINS))
    return added
