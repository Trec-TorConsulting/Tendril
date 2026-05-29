"""Seed plant_health_treatments table from existing treatment_db.py data.

Run via: python -m app.data.seed_treatments
Or call seed_treatments(session) from migration/startup code.
"""

from __future__ import annotations

import asyncio
import dataclasses
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.treatment_db import TREATMENT_DATABASE
from app.database import async_session_factory

logger = logging.getLogger("tendril.seed.treatments")


async def seed_treatments(session: AsyncSession) -> int:
    """Upsert all treatment entries into the plant_health_treatments table.

    Returns count of upserted rows.
    """
    count = 0
    for entry in TREATMENT_DATABASE:
        data = dataclasses.asdict(entry)
        entry_id = data.pop("id")

        # Use INSERT ... ON CONFLICT DO UPDATE for idempotent seeding
        stmt = text("""
            INSERT INTO plant_health_treatments (id, category, name, aka, summary, symptoms,
                identification_tips, causes, severity_criteria, treatments, prevention,
                recovery_time, commonly_confused_with, updated_at)
            VALUES (:id, :category, :name, :aka::jsonb, :summary, :symptoms::jsonb,
                :identification_tips::jsonb, :causes::jsonb, :severity_criteria::jsonb,
                :treatments::jsonb, :prevention::jsonb, :recovery_time,
                :commonly_confused_with::jsonb, now())
            ON CONFLICT (id) DO UPDATE SET
                category = EXCLUDED.category,
                name = EXCLUDED.name,
                aka = EXCLUDED.aka,
                summary = EXCLUDED.summary,
                symptoms = EXCLUDED.symptoms,
                identification_tips = EXCLUDED.identification_tips,
                causes = EXCLUDED.causes,
                severity_criteria = EXCLUDED.severity_criteria,
                treatments = EXCLUDED.treatments,
                prevention = EXCLUDED.prevention,
                recovery_time = EXCLUDED.recovery_time,
                commonly_confused_with = EXCLUDED.commonly_confused_with,
                updated_at = now()
        """)

        import json

        await session.execute(
            stmt,
            {
                "id": entry_id,
                "category": data["category"],
                "name": data["name"],
                "aka": json.dumps(data["aka"]),
                "summary": data["summary"],
                "symptoms": json.dumps(data["symptoms"]),
                "identification_tips": json.dumps(data["identification_tips"]),
                "causes": json.dumps(data["causes"]),
                "severity_criteria": json.dumps(data["severity_criteria"]),
                "treatments": json.dumps(data["treatments"]),
                "prevention": json.dumps(data["prevention"]),
                "recovery_time": data["recovery_time"],
                "commonly_confused_with": json.dumps(data["commonly_confused_with"]),
            },
        )
        count += 1

    await session.commit()
    logger.info("Seeded %d plant health treatments", count)
    return count


async def _main() -> None:
    async with async_session_factory() as session:
        await seed_treatments(session)


if __name__ == "__main__":
    asyncio.run(_main())
