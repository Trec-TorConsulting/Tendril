"""Auto-task generation engine — creates grow-type and stage-aware tasks."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.commercial.models import Task
from app.grows.models import Bucket, FeedingSchedule, GrowCycle, Strain
from app.tenants.models import User

logger = logging.getLogger("tendril.tasks.autogen")

# ── Task templates by category ──────────────────────────────────────

HYDRO_TYPES = {"dwc", "rdwc", "nft", "ebb_flow", "drip", "aeroponics", "kratky"}
SOIL_TYPES = {"soil", "outdoor", "container"}
COCO_TYPES = {"coco", "rockwool"}

# (category, title, description, interval_days, priority, grow_types_or_None, stages_or_None)
TASK_TEMPLATES: list[tuple[str, str, str, int, str, set[str] | None, set[str] | None]] = [
    # Universal
    ("health_check", "Inspect plants for health issues", "Check leaves, stems, roots for discoloration, pests, or wilting.", 1, "medium", None, None),
    ("pest_check", "Check for pests & mold", "Inspect undersides of leaves, base of stems, and soil/medium surface for pests or mold.", 3, "medium", None, None),

    # Hydro-specific
    ("ph_check", "Check pH levels", "Test reservoir pH and adjust to target range.", 1, "high", HYDRO_TYPES, None),
    ("ec_check", "Check EC/PPM levels", "Measure EC/PPM and adjust nutrient concentration.", 1, "high", HYDRO_TYPES, None),
    ("flush_and_fill", "Flush & Fill reservoir", None, 7, "high", HYDRO_TYPES, None),  # description built dynamically
    ("water_temp", "Check water temperature", "Verify reservoir temp is 65-72°F. Add ice or chiller if needed.", 1, "medium", {"dwc", "rdwc", "nft"}, None),
    ("top_off", "Top off reservoir", "Add pH'd water to maintain reservoir level.", 2, "medium", {"dwc", "rdwc"}, None),

    # Soil-specific
    ("ph_check", "Check soil/runoff pH", "Test runoff pH after watering.", 3, "medium", SOIL_TYPES, None),
    ("watering", "Check soil moisture & water", "Check soil moisture at 2-3 inch depth. Water if dry.", 1, "high", SOIL_TYPES, None),
    ("top_dress", "Top dress nutrients", "Apply dry amendments to soil surface.", 14, "low", {"soil"}, {"vegetative", "flowering"}),

    # Coco/Rockwool
    ("ph_check", "Check runoff pH", "Measure runoff pH after fertigation.", 1, "high", COCO_TYPES, None),
    ("ec_check", "Check runoff EC", "Measure runoff EC to detect salt buildup.", 1, "high", COCO_TYPES, None),
    ("calmag", "CalMag supplement check", "Coco strips calcium — verify CalMag levels are adequate.", 3, "medium", {"coco"}, None),

    # Stage-specific (all types)
    ("defoliation", "Defoliation / training", "Remove large fan leaves blocking bud sites. LST/HST as needed.", 7, "low", None, {"vegetative"}),
    ("trichome_check", "Check trichomes", "Use loupe/microscope to check trichome color (clear → cloudy → amber).", 2, "high", None, {"late_flower", "ripening"}),
    ("flush", "Begin flush (plain water)", "Switch to plain pH'd water for final flush before harvest.", 1, "urgent", None, {"flush"}),
]


async def _get_tenant_owner(session: AsyncSession, tenant_id: UUID) -> UUID | None:
    """Find the owner user for a tenant."""
    result = await session.execute(
        select(User.id).where(User.tenant_id == tenant_id, User.role == "owner").limit(1)
    )
    row = result.scalar_one_or_none()
    return row


async def _task_exists(
    session: AsyncSession,
    tenant_id: UUID,
    category: str,
    grow_cycle_id: UUID,
    due_date: datetime,
) -> bool:
    """Check if a pending/in_progress auto-task already exists for this category+grow+date."""
    result = await session.execute(
        select(Task.id).where(
            Task.tenant_id == tenant_id,
            Task.category == category,
            Task.grow_cycle_id == grow_cycle_id,
            Task.source == "auto",
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date >= due_date.replace(hour=0, minute=0, second=0),
            Task.due_date < due_date.replace(hour=0, minute=0, second=0) + timedelta(days=1),
        ).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def _build_flush_fill_description(
    session: AsyncSession,
    grow: GrowCycle,
) -> str:
    """Build a nutrient recipe description for a flush & fill task.

    Pulls the feeding schedule for the current stage and active bucket volumes
    to produce a concrete mixing guide.
    """
    lines = ["Drain reservoir completely, rinse, and refill with fresh nutrient solution."]

    # Get total volume from active buckets
    vol_row = await session.execute(
        select(func.sum(Bucket.volume_gallons))
        .where(Bucket.grow_cycle_id == grow.id, Bucket.status == "active")
    )
    total_gallons = vol_row.scalar_one_or_none()

    # Get feeding schedule for current stage
    feed = (await session.execute(
        select(FeedingSchedule)
        .where(
            FeedingSchedule.grow_cycle_id == grow.id,
            FeedingSchedule.stage == grow.stage,
        )
        .order_by(FeedingSchedule.created_at.desc())
        .limit(1)
    )).scalar_one_or_none()

    if total_gallons:
        lines.append(f"\nTotal volume: {total_gallons:.1f} gal")

    if feed:
        lines.append(f"\n--- Nutrients ({feed.name} — {grow.stage}) ---")
        if feed.target_ppm:
            lines.append(f"Target PPM: {feed.target_ppm:.0f}")
        if feed.target_ec:
            lines.append(f"Target EC: {feed.target_ec:.2f}")

        nutrients = feed.nutrients if isinstance(feed.nutrients, list) else []
        for n in nutrients:
            name = n.get("name", "Unknown")
            ml_per_gal = n.get("ml_per_gallon", 0)
            brand = n.get("brand", "")
            strength = n.get("strength_pct")
            if total_gallons and ml_per_gal:
                total_ml = ml_per_gal * total_gallons
                line = f"  • {name}: {ml_per_gal} ml/gal × {total_gallons:.1f} gal = {total_ml:.1f} ml"
            else:
                line = f"  • {name}: {ml_per_gal} ml/gal"
            if brand:
                line += f" ({brand})"
            if strength and strength != 100:
                line += f" @ {strength}%"
            lines.append(line)

        if feed.notes:
            lines.append(f"\nNote: {feed.notes}")
    else:
        lines.append("\nNo feeding schedule found for this stage — mix nutrients per your usual recipe.")

    lines.append("\npH to 5.8-6.2 after mixing. Let solution aerate before adding to reservoir.")
    return "\n".join(lines)


async def generate_tasks_for_grow(
    session: AsyncSession,
    grow: GrowCycle,
    horizon_days: int = 7,
) -> int:
    """Generate auto-tasks for a grow cycle up to horizon_days ahead.

    Returns number of tasks created.
    """
    owner_id = await _get_tenant_owner(session, grow.tenant_id)
    if not owner_id:
        logger.warning("No owner found for tenant %s — skipping task generation", grow.tenant_id)
        return 0

    now = datetime.now(timezone.utc)
    created = 0

    for category, title, description, interval, priority, grow_types, stages in TASK_TEMPLATES:
        # Filter by grow type
        if grow_types and grow.grow_type not in grow_types:
            continue
        # Filter by stage
        if stages and grow.stage not in stages:
            continue

        # Generate tasks for each interval within horizon
        for day_offset in range(0, horizon_days, interval):
            due = now + timedelta(days=day_offset)
            due = due.replace(hour=9, minute=0, second=0, microsecond=0)  # default 9 AM

            if await _task_exists(session, grow.tenant_id, category, grow.id, due):
                continue

            # Build dynamic description for flush & fill tasks
            task_description = description
            if category == "flush_and_fill":
                task_description = await _build_flush_fill_description(session, grow)

            task = Task(
                tenant_id=grow.tenant_id,
                title=title,
                description=task_description,
                status="pending",
                priority=priority,
                category=category,
                source="auto",
                created_by=owner_id,
                grow_cycle_id=grow.id,
                tent_id=grow.tent_id,
                due_date=due,
            )
            session.add(task)
            created += 1

    # ── Strain-based harvest tasks ──────────────────────────────
    if grow.stage in ("flowering", "late_flower", "ripening"):
        milestones = grow.milestones or {}
        flowering_start_str = milestones.get("flowering") or milestones.get("flower")
        if flowering_start_str:
            flowering_start = datetime.fromisoformat(flowering_start_str)
            if flowering_start.tzinfo is None:
                flowering_start = flowering_start.replace(tzinfo=timezone.utc)

            # Find strain flowering_days from buckets
            buckets = (await session.execute(
                select(Bucket)
                .where(Bucket.grow_cycle_id == grow.id, Bucket.status == "active", Bucket.strain_id.isnot(None))
            )).scalars().all()

            for bucket in buckets:
                strain = bucket.strain or await session.get(Strain, bucket.strain_id)
                if not strain or not strain.flowering_days:
                    continue

                est_harvest = flowering_start + timedelta(days=strain.flowering_days)
                days_remaining = (est_harvest - now).days

                # Flush reminder at 10 days before harvest
                if 0 < days_remaining <= 10:
                    flush_due = est_harvest - timedelta(days=10)
                    flush_due = flush_due.replace(hour=9, minute=0, second=0, microsecond=0)
                    if flush_due >= now and not await _task_exists(session, grow.tenant_id, "flush_start", grow.id, flush_due):
                        task = Task(
                            tenant_id=grow.tenant_id,
                            title=f"Start flush — {strain.name}",
                            description=f"{strain.name} ({strain.flowering_days}d flower) estimated harvest in ~{days_remaining} days. Begin plain water flush.",
                            status="pending",
                            priority="high",
                            category="flush_start",
                            source="auto",
                            created_by=owner_id,
                            grow_cycle_id=grow.id,
                            bucket_id=bucket.id,
                            due_date=flush_due,
                        )
                        session.add(task)
                        created += 1

                # Harvest day task
                if -1 <= days_remaining <= 1:
                    harvest_due = est_harvest.replace(hour=9, minute=0, second=0, microsecond=0)
                    if not await _task_exists(session, grow.tenant_id, "harvest", grow.id, harvest_due):
                        task = Task(
                            tenant_id=grow.tenant_id,
                            title=f"Harvest — {strain.name}",
                            description=f"{strain.name} has reached its estimated {strain.flowering_days}-day flowering window. Check trichomes and harvest.",
                            status="pending",
                            priority="urgent",
                            category="harvest",
                            source="auto",
                            created_by=owner_id,
                            grow_cycle_id=grow.id,
                            bucket_id=bucket.id,
                            due_date=harvest_due,
                        )
                        session.add(task)
                        created += 1

    return created


async def generate_all_tasks(session: AsyncSession) -> int:
    """Generate auto-tasks for all active grows."""
    grows = (await session.execute(
        select(GrowCycle).where(GrowCycle.status == "active")
    )).scalars().all()

    total = 0
    for grow in grows:
        try:
            count = await generate_tasks_for_grow(session, grow)
            total += count
        except Exception:
            logger.exception("Task generation failed for grow %s", grow.id)

    await session.commit()
    return total
