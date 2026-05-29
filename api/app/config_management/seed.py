"""Seed grow type configs, task templates from existing hardcoded data into DB tables.

Run standalone: python -m app.config_management.seed
Or called from Alembic data migration / startup.
"""

from __future__ import annotations

import asyncio
import logging
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("tendril.config_management.seed")


def _extract_env_value(val) -> float | None:
    """Extract a numeric value from environment dict entries (may be dict with target, or scalar)."""
    if val is None:
        return None
    if isinstance(val, dict):
        return val.get("target") or val.get("min")
    if isinstance(val, int | float):
        return float(val)
    return None


def _extract_env_range(val) -> tuple[float | None, float | None]:
    """Extract min/max from environment dict entries."""
    if val is None:
        return None, None
    if isinstance(val, dict):
        return val.get("min"), val.get("max")
    if isinstance(val, int | float):
        return float(val), float(val)
    return None, None


async def seed_grow_type_profiles(session: AsyncSession) -> int:
    """Seed grow_type_profiles from grows/grow_types.py GROW_TYPE_PROFILES."""
    import json

    from app.grows.grow_type_configs import GROW_TYPE_CONFIGS
    from app.grows.grow_types import GROW_TYPE_PROFILES

    count = 0
    for profile in GROW_TYPE_PROFILES:
        profile_id = uuid.uuid4()
        slug = profile["id"]

        # Build extended_config from grow_type_configs (scale_tiers, thresholds, etc.)
        # and profile-level fields not in dedicated columns
        full_config = GROW_TYPE_CONFIGS.get(slug, {})
        extended = {}
        # From grow_type_configs (rich per-stage config data)
        for key in (
            "scale_tiers",
            "strain_adjustments",
            "monitoring_thresholds",
            "quick_reference",
            "advanced_techniques",
            "nutrient_brands",
            "water_source_profiles",
            "harvest_decision_matrix",
            "post_harvest_guide",
            "reservoir_management",
        ):
            if key in full_config:
                extended[key] = full_config[key]
        # From profile (AI context fields)
        for key in (
            "terminology",
            "relevant_sensors",
            "primary_sensors",
            "irrelevant_sensors",
            "unique_fields",
            "ph_range",
            "ec_range",
            "health_check_questions",
            "automations",
            "feeding_approach",
            "nutrient_strength",
            "common_problems",
            "category",
        ):
            if key in profile:
                extended[key] = profile[key]

        await session.execute(
            text("""
                INSERT INTO grow_type_profiles
                    (id, name, slug, description, sensor_kit, ai_context_prompt, is_system, extended_config)
                VALUES (:id, :name, :slug, :description, :sensor_kit, :ai_context_prompt, true, :extended_config)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    sensor_kit = EXCLUDED.sensor_kit,
                    ai_context_prompt = EXCLUDED.ai_context_prompt,
                    extended_config = EXCLUDED.extended_config,
                    updated_at = now()
            """),
            {
                "id": str(profile_id),
                "name": profile["name"],
                "slug": slug,
                "description": profile.get("description", ""),
                "sensor_kit": profile.get("sensor_kit"),
                "ai_context_prompt": profile.get("ai_prompt_context"),
                "extended_config": json.dumps(extended) if extended else None,
            },
        )
        count += 1
    await session.commit()
    logger.info("Seeded %d grow type profiles", count)
    return count


async def seed_grow_type_stages(session: AsyncSession) -> int:
    """Seed stages, environment, nutrients, watering from grow_type_configs."""
    from app.grows.grow_type_configs import GROW_TYPE_CONFIGS

    total_stages = 0

    for grow_type_id, config in GROW_TYPE_CONFIGS.items():
        # Get profile ID from DB
        result = await session.execute(
            text("SELECT id FROM grow_type_profiles WHERE slug = :slug"),
            {"slug": grow_type_id},
        )
        row = result.first()
        if not row:
            logger.warning("Profile not found for %s, skipping stages", grow_type_id)
            continue
        profile_id = str(row[0])

        stages = config.get("stages", [])
        for stage in stages:
            stage_id = str(uuid.uuid4())
            duration = stage.get("duration_days", {})

            await session.execute(
                text("""
                    INSERT INTO grow_type_stages
                        (id, profile_id, name, slug, "order",
                         duration_days_min, duration_days_max, description, tips)
                    VALUES (:id, :profile_id, :name, :slug, :order,
                            :duration_min, :duration_max, :description, :tips)
                    ON CONFLICT ON CONSTRAINT uq_grow_type_stage_profile_slug DO UPDATE SET
                        name = EXCLUDED.name,
                        "order" = EXCLUDED."order",
                        duration_days_min = EXCLUDED.duration_days_min,
                        duration_days_max = EXCLUDED.duration_days_max,
                        description = EXCLUDED.description,
                        tips = EXCLUDED.tips
                    RETURNING id
                """),
                {
                    "id": stage_id,
                    "profile_id": profile_id,
                    "name": stage.get("name", ""),
                    "slug": stage.get("id", ""),
                    "order": stage.get("order", 0),
                    "duration_min": duration.get("min") if isinstance(duration, dict) else None,
                    "duration_max": duration.get("max") if isinstance(duration, dict) else None,
                    "description": stage.get("description", ""),
                    "tips": None,
                },
            )

            # Get the actual stage ID (in case of upsert)
            result = await session.execute(
                text("SELECT id FROM grow_type_stages WHERE profile_id = :pid AND slug = :slug"),
                {"pid": profile_id, "slug": stage.get("id", "")},
            )
            actual_stage_id = str(result.scalar_one())

            # ─── Environment ───
            env = stage.get("environment")
            if env:
                temp_day = env.get("temp_day_f", {})
                temp_night = env.get("temp_night_f", {})
                humidity = env.get("humidity_pct", {})
                vpd = env.get("vpd_kpa")
                light_ppfd = env.get("light_ppfd")

                temp_min, temp_max = _extract_env_range(temp_night)
                _, temp_max_day = _extract_env_range(temp_day)
                if temp_max_day and (temp_max is None or temp_max_day > temp_max):
                    temp_max = temp_max_day
                temp_ideal = _extract_env_value(temp_day)

                hum_min, hum_max = _extract_env_range(humidity)
                hum_ideal = _extract_env_value(humidity)

                vpd_min, vpd_max = _extract_env_range(vpd)
                ppfd_min, ppfd_max = _extract_env_range(light_ppfd)

                light_hours = env.get("light_hours")
                light_hours = None if isinstance(light_hours, str) else (float(light_hours) if light_hours else None)

                # Water temp from reservoir if available
                reservoir = stage.get("reservoir")
                water_temp_min = water_temp_max = None
                if reservoir and isinstance(reservoir, dict):
                    wt = reservoir.get("water_temp_f", {})
                    water_temp_min, water_temp_max = _extract_env_range(wt)

                await session.execute(
                    text("""
                        INSERT INTO grow_type_environment (id, stage_id, temp_min, temp_max, temp_ideal,
                            humidity_min, humidity_max, humidity_ideal, vpd_min, vpd_max,
                            light_hours, light_ppfd_min, light_ppfd_max, co2_min, co2_max,
                            water_temp_min, water_temp_max)
                        VALUES (:id, :stage_id, :temp_min, :temp_max, :temp_ideal,
                            :hum_min, :hum_max, :hum_ideal, :vpd_min, :vpd_max,
                            :light_hours, :ppfd_min, :ppfd_max, :co2_min, :co2_max,
                            :water_temp_min, :water_temp_max)
                        ON CONFLICT ON CONSTRAINT uq_grow_type_environment_stage DO UPDATE SET
                            temp_min = EXCLUDED.temp_min, temp_max = EXCLUDED.temp_max,
                            temp_ideal = EXCLUDED.temp_ideal, humidity_min = EXCLUDED.humidity_min,
                            humidity_max = EXCLUDED.humidity_max, humidity_ideal = EXCLUDED.humidity_ideal,
                            vpd_min = EXCLUDED.vpd_min, vpd_max = EXCLUDED.vpd_max,
                            light_hours = EXCLUDED.light_hours, light_ppfd_min = EXCLUDED.light_ppfd_min,
                            light_ppfd_max = EXCLUDED.light_ppfd_max,
                            co2_min = EXCLUDED.co2_min, co2_max = EXCLUDED.co2_max,
                            water_temp_min = EXCLUDED.water_temp_min, water_temp_max = EXCLUDED.water_temp_max
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "stage_id": actual_stage_id,
                        "temp_min": temp_min,
                        "temp_max": temp_max,
                        "temp_ideal": temp_ideal,
                        "hum_min": hum_min,
                        "hum_max": hum_max,
                        "hum_ideal": hum_ideal,
                        "vpd_min": vpd_min,
                        "vpd_max": vpd_max,
                        "light_hours": light_hours,
                        "ppfd_min": ppfd_min,
                        "ppfd_max": ppfd_max,
                        "co2_min": None,
                        "co2_max": None,
                        "water_temp_min": water_temp_min,
                        "water_temp_max": water_temp_max,
                    },
                )

            # ─── Nutrients ───
            nutrients = stage.get("nutrients")
            if nutrients and isinstance(nutrients, dict):
                # Store as a single week-1 entry for this stage
                reservoir = stage.get("reservoir", {}) or {}

                ec_target = None
                ec_min = ec_max = None
                ph_target = ph_min = ph_max = None

                if isinstance(reservoir, dict):
                    ec_data = reservoir.get("ec", {})
                    if isinstance(ec_data, dict):
                        ec_min = ec_data.get("min")
                        ec_max = ec_data.get("max")
                        ec_target = ec_data.get("target")
                    ph_data = reservoir.get("ph", {})
                    if isinstance(ph_data, dict):
                        ph_min = ph_data.get("min")
                        ph_max = ph_data.get("max")
                        ph_target = ph_data.get("target")

                base_nutrients = {
                    k: v for k, v in nutrients.items() if k.endswith("_ml_per_gal") or k in ("strength_pct", "approach")
                }
                supplements = nutrients.get("supplements")

                await session.execute(
                    text("""
                        INSERT INTO grow_type_nutrients (id, stage_id, week, ec_min, ec_max, ec_target,
                            ph_min, ph_max, ph_target, base_nutrients, supplements, notes)
                        VALUES (:id, :stage_id, 1, :ec_min, :ec_max, :ec_target,
                            :ph_min, :ph_max, :ph_target, :base_nutrients::jsonb, :supplements::jsonb, :notes)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "stage_id": actual_stage_id,
                        "ec_min": ec_min,
                        "ec_max": ec_max,
                        "ec_target": ec_target,
                        "ph_min": ph_min,
                        "ph_max": ph_max,
                        "ph_target": ph_target,
                        "base_nutrients": __import__("json").dumps(base_nutrients) if base_nutrients else None,
                        "supplements": __import__("json").dumps(supplements) if supplements else None,
                        "notes": nutrients.get("approach"),
                    },
                )

            # ─── Watering ───
            medium = stage.get("medium")
            reservoir = stage.get("reservoir")
            if medium and isinstance(medium, dict):
                await session.execute(
                    text("""
                        INSERT INTO grow_type_watering
                            (id, stage_id, method, frequency_hours,
                             volume_ml, runoff_target_pct, notes)
                        VALUES (:id, :stage_id, :method, NULL, NULL, NULL, :notes)
                        ON CONFLICT ON CONSTRAINT uq_grow_type_watering_stage DO UPDATE SET
                            method = EXCLUDED.method, notes = EXCLUDED.notes
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "stage_id": actual_stage_id,
                        "method": medium.get("watering_method", ""),
                        "notes": medium.get("notes", ""),
                    },
                )
            elif reservoir and isinstance(reservoir, dict):
                change_days = reservoir.get("change_interval_days")
                freq_hours = change_days * 24 if change_days else None
                await session.execute(
                    text("""
                        INSERT INTO grow_type_watering
                            (id, stage_id, method, frequency_hours,
                             volume_ml, runoff_target_pct, notes)
                        VALUES (:id, :stage_id, 'reservoir_change',
                                :freq, NULL, NULL, :notes)
                        ON CONFLICT ON CONSTRAINT uq_grow_type_watering_stage DO UPDATE SET
                            method = EXCLUDED.method, frequency_hours = EXCLUDED.frequency_hours, notes = EXCLUDED.notes
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "stage_id": actual_stage_id,
                        "method": "reservoir_change",
                        "freq": freq_hours,
                        "notes": reservoir.get("notes", ""),
                    },
                )

            total_stages += 1

    await session.commit()
    logger.info("Seeded %d grow type stages with environment/nutrients/watering", total_stages)
    return total_stages


async def seed_grow_type_equipment(session: AsyncSession) -> int:
    """Seed equipment lists from grow_type_configs."""
    from app.grows.grow_type_configs import GROW_TYPE_CONFIGS

    count = 0
    for grow_type_id, config in GROW_TYPE_CONFIGS.items():
        result = await session.execute(
            text("SELECT id FROM grow_type_profiles WHERE slug = :slug"),
            {"slug": grow_type_id},
        )
        row = result.first()
        if not row:
            continue
        profile_id = str(row[0])

        for item in config.get("equipment", []):
            category = item.get("category", "essential")
            required = category == "essential"
            await session.execute(
                text("""
                    INSERT INTO grow_type_equipment (id, profile_id, item_name, category, required, notes)
                    VALUES (:id, :profile_id, :item_name, :category, :required, :notes)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "profile_id": profile_id,
                    "item_name": item.get("name", ""),
                    "category": category,
                    "required": required,
                    "notes": item.get("description", ""),
                },
            )
            count += 1

    await session.commit()
    logger.info("Seeded %d equipment items", count)
    return count


async def seed_grow_type_troubleshooting(session: AsyncSession) -> int:
    """Seed troubleshooting entries from grow_type_configs."""
    from app.grows.grow_type_configs import GROW_TYPE_CONFIGS

    count = 0
    for grow_type_id, config in GROW_TYPE_CONFIGS.items():
        result = await session.execute(
            text("SELECT id FROM grow_type_profiles WHERE slug = :slug"),
            {"slug": grow_type_id},
        )
        row = result.first()
        if not row:
            continue
        profile_id = str(row[0])

        for category_block in config.get("troubleshooting", []):
            if not isinstance(category_block, dict):
                continue
            for problem in category_block.get("problems", []):
                await session.execute(
                    text("""
                        INSERT INTO grow_type_troubleshooting (id, profile_id, symptom, cause, solution, severity)
                        VALUES (:id, :profile_id, :symptom, :cause, :solution, :severity)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "profile_id": profile_id,
                        "symptom": problem.get("symptom", ""),
                        "cause": "; ".join(problem.get("causes", []))
                        if isinstance(problem.get("causes"), list)
                        else problem.get("diagnosis", ""),
                        "solution": "; ".join(problem.get("solutions", []))
                        if isinstance(problem.get("solutions"), list)
                        else "",
                        "severity": problem.get("severity", "medium"),
                    },
                )
                count += 1

    await session.commit()
    logger.info("Seeded %d troubleshooting entries", count)
    return count


async def seed_task_templates(session: AsyncSession) -> int:
    """Seed task templates from scheduler/task_generator.py."""
    from app.scheduler.task_generator import TASK_TEMPLATES

    count = 0
    for tmpl in TASK_TEMPLATES:
        grow_types = list(tmpl.grow_types) if tmpl.grow_types else None
        stages_list = list(tmpl.stages) if tmpl.stages else None
        # Use first stage as stage_slug (templates can apply to multiple but we store primary)
        stage_slug = stages_list[0] if stages_list and len(stages_list) == 1 else None

        template_id = str(uuid.uuid4())
        await session.execute(
            text("""
                INSERT INTO task_templates (id, name, description, category, grow_type_slugs,
                    frequency_hours, stage_slug, priority, routine, estimated_minutes, is_system)
                VALUES (:id, :name, :description, :category, :grow_type_slugs,
                    :frequency_hours, :stage_slug, :priority, :routine, :estimated_minutes, true)
            """),
            {
                "id": template_id,
                "name": tmpl.title,
                "description": tmpl.detail or tmpl.brief,
                "category": tmpl.category,
                "grow_type_slugs": grow_types,
                "frequency_hours": tmpl.interval_days * 24 if tmpl.interval_days > 0 else 0,
                "stage_slug": stage_slug,
                "priority": tmpl.priority,
                "routine": tmpl.routine,
                "estimated_minutes": tmpl.estimated_minutes,
            },
        )

        # Add brief as a single step
        await session.execute(
            text("""
                INSERT INTO task_template_steps (id, template_id, "order", instruction, duration_minutes, optional)
                VALUES (:id, :template_id, 1, :instruction, :duration, false)
            """),
            {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "instruction": tmpl.brief,
                "duration": tmpl.estimated_minutes,
            },
        )
        count += 1

    await session.commit()
    logger.info("Seeded %d task templates", count)
    return count


async def seed_stage_transition_tasks(session: AsyncSession) -> int:
    """Seed stage transition tasks from STAGE_TRANSITION_TASKS."""
    from app.scheduler.task_generator import (
        STAGE_TRANSITION_TASKS,
    )

    count = 0
    for stage, tasks in STAGE_TRANSITION_TASKS.items():
        for title, brief, priority, routine, est_minutes, grow_types in tasks:
            # Convert set to sorted list for stable DB storage
            slugs = sorted(grow_types) if grow_types else None
            await session.execute(
                text("""
                    INSERT INTO stage_transition_tasks
                        (id, stage, title, brief, priority, routine, estimated_minutes, grow_type_slugs, is_system)
                    VALUES (:id, :stage, :title, :brief, :priority, :routine, :est_min, :slugs, true)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "id": str(uuid.uuid4()),
                    "stage": stage,
                    "title": title,
                    "brief": brief,
                    "priority": priority,
                    "routine": routine,
                    "est_min": est_minutes,
                    "slugs": slugs,
                },
            )
            count += 1

    await session.commit()
    logger.info("Seeded %d stage transition tasks", count)
    return count


async def seed_automation_suppressions(session: AsyncSession) -> int:
    """Seed automation suppressions and verify tasks."""
    import json

    from app.scheduler.task_generator import AUTOMATION_SUPPRESSIONS, AUTOMATION_VERIFY_TASKS

    count = 0
    for automation_key, suppressed in AUTOMATION_SUPPRESSIONS.items():
        verify_task = AUTOMATION_VERIFY_TASKS.get(automation_key)
        verify_json = None
        if verify_task:
            verify_json = {
                "category": verify_task.category,
                "title": verify_task.title,
                "brief": verify_task.brief,
                "detail": verify_task.detail,
                "interval_days": verify_task.interval_days,
                "priority": verify_task.priority,
                "routine": verify_task.routine,
                "estimated_minutes": verify_task.estimated_minutes,
            }

        await session.execute(
            text("""
                INSERT INTO automation_suppressions
                    (id, automation_key, suppressed_categories, verify_task, is_system)
                VALUES (:id, :key, :suppressed, :verify_task, true)
                ON CONFLICT (automation_key) DO UPDATE SET
                    suppressed_categories = EXCLUDED.suppressed_categories,
                    verify_task = EXCLUDED.verify_task
            """),
            {
                "id": str(uuid.uuid4()),
                "key": automation_key,
                "suppressed": suppressed,
                "verify_task": json.dumps(verify_json) if verify_json else None,
            },
        )
        count += 1

    await session.commit()
    logger.info("Seeded %d automation suppressions", count)
    return count


async def seed_companion_plants(session: AsyncSession) -> int:
    """Seed companion plants from data/companion_plants.py."""
    from app.data.companion_plants import COMPANION_DB

    count = 0
    for plant_name, data in COMPANION_DB.items():
        slug = plant_name.lower().replace(" ", "_")
        # Derive a category from context
        category = (
            "herb"
            if plant_name in {"basil", "dill", "peppermint", "chamomile", "lavender", "lemon_balm", "chives", "yarrow"}
            else "flower"
            if plant_name in {"marigold", "sunflower"}
            else "cover_crop"
            if plant_name in {"clover", "alfalfa", "cerastium"}
            else "vegetable"
            if plant_name in {"beans", "garlic"}
            else "plant"
        )

        await session.execute(
            text("""
                INSERT INTO companion_plants
                    (id, name, slug, category, benefits, companions, antagonists, notes, is_system)
                VALUES (:id, :name, :slug, :category, :benefits, :companions, :antagonists, :notes, true)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    benefits = EXCLUDED.benefits,
                    companions = EXCLUDED.companions,
                    antagonists = EXCLUDED.antagonists,
                    notes = EXCLUDED.notes
            """),
            {
                "id": str(uuid.uuid4()),
                "name": plant_name.replace("_", " ").title(),
                "slug": slug,
                "category": category,
                "benefits": data.get("beneficial", []),
                "companions": data.get("beneficial", []),
                "antagonists": data.get("harmful", []),
                "notes": data.get("notes", ""),
            },
        )
        count += 1

    await session.commit()
    logger.info("Seeded %d companion plants", count)
    return count


async def seed_feed_charts(session: AsyncSession) -> int:
    """Seed feed charts from reference/feed_charts.py."""
    import json

    from app.reference.feed_charts import FEED_CHARTS

    count = 0
    for chart in FEED_CHARTS:
        await session.execute(
            text("""
                INSERT INTO feed_charts
                    (id, brand, line, medium, products, schedule, notes, is_system)
                VALUES (:id, :brand, :line, :medium, :products, :schedule, :notes, true)
                ON CONFLICT ON CONSTRAINT uq_feed_chart_brand_line DO UPDATE SET
                    medium = EXCLUDED.medium,
                    products = EXCLUDED.products,
                    schedule = EXCLUDED.schedule,
                    notes = EXCLUDED.notes
            """),
            {
                "id": str(uuid.uuid4()),
                "brand": chart["brand"],
                "line": chart["line"],
                "medium": chart["medium"],
                "products": chart["products"],
                "schedule": json.dumps(chart["schedule"]),
                "notes": chart.get("notes", ""),
            },
        )
        count += 1

    await session.commit()
    logger.info("Seeded %d feed charts", count)
    return count


async def seed_all(session: AsyncSession) -> dict[str, int]:
    """Run all seeders in order. Returns counts."""
    results = {}
    results["profiles"] = await seed_grow_type_profiles(session)
    results["stages"] = await seed_grow_type_stages(session)
    results["equipment"] = await seed_grow_type_equipment(session)
    results["troubleshooting"] = await seed_grow_type_troubleshooting(session)
    results["task_templates"] = await seed_task_templates(session)
    results["stage_transitions"] = await seed_stage_transition_tasks(session)
    results["automation_suppressions"] = await seed_automation_suppressions(session)
    results["companion_plants"] = await seed_companion_plants(session)
    results["feed_charts"] = await seed_feed_charts(session)
    return results


async def main():
    """Standalone entry point."""
    import os

    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://tendril:tendril@localhost:5432/tendril")

    from app.database import async_session_factory
    from app.logging_config import setup_logging

    setup_logging("INFO")

    async with async_session_factory() as session:
        await seed_all(session)


if __name__ == "__main__":
    asyncio.run(main())
