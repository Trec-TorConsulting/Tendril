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
    """Check if an auto-task already exists for this category+grow+date.

    Checks ALL statuses (pending, in_progress, completed) so completed tasks
    are not re-created by the next scheduler run.
    """
    day_start = due_date.replace(hour=0, minute=0, second=0)
    result = await session.execute(
        select(Task.id).where(
            Task.tenant_id == tenant_id,
            Task.category == category,
            Task.grow_cycle_id == grow_cycle_id,
            Task.source == "auto",
            Task.due_date >= day_start,
            Task.due_date < day_start + timedelta(days=1),
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


# ── Health eval → tasks ──────────────────────────────────────────────

async def create_tasks_from_health_eval(
    session: AsyncSession,
    grow: GrowCycle,
    score: int | None,
    issues: list[str],
    actions: list[str],
) -> int:
    """Create tasks from health evaluation results.

    Each action becomes a concrete task the grower can check off.
    Priority is derived from the health score.
    """
    owner_id = await _get_tenant_owner(session, grow.tenant_id)
    if not owner_id:
        return 0

    now = datetime.now(timezone.utc)
    created = 0

    # Derive priority from health score
    if score is not None:
        if score < 50:
            priority = "urgent"
        elif score < 70:
            priority = "high"
        elif score < 85:
            priority = "medium"
        else:
            priority = "low"
    else:
        priority = "medium"

    # Check for existing unresolved AI tasks for this grow to avoid duplicates
    existing_ai_tasks = (await session.execute(
        select(Task.title)
        .where(
            Task.grow_cycle_id == grow.id,
            Task.source == "ai",
            Task.category == "health_response",
            Task.status.in_(["pending", "in_progress"]),
        )
    )).scalars().all()
    existing_titles = {t.lower().strip() for t in existing_ai_tasks}

    for action in actions:
        # Skip if a very similar task already exists
        action_lower = action.lower().strip()
        if any(_similar(action_lower, existing) for existing in existing_titles):
            continue

        # Build description from issues context
        related_issues = [i for i in issues if _related(action, i)]
        desc_parts = [action]
        if related_issues:
            desc_parts.append("\nRelated issues from health check:")
            for issue in related_issues:
                desc_parts.append(f"  • {issue}")
        if score is not None:
            desc_parts.append(f"\nHealth score: {score}/100")

        task = Task(
            tenant_id=grow.tenant_id,
            title=action[:500],
            description="\n".join(desc_parts),
            status="pending",
            priority=priority,
            category="health_response",
            source="ai",
            created_by=owner_id,
            grow_cycle_id=grow.id,
            tent_id=grow.tent_id,
            due_date=now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1 if now.hour >= 9 else 0),
        )
        session.add(task)
        existing_titles.add(action_lower)
        created += 1

    if created:
        await session.commit()
        logger.info("Created %d AI tasks from health eval (score=%s) for grow %s", created, score, grow.id)

    return created


def _similar(a: str, b: str) -> bool:
    """Quick similarity check — if first 40 chars match, consider it a duplicate."""
    return a[:40] == b[:40]


def _related(action: str, issue: str) -> bool:
    """Check if an action is related to an issue by keyword overlap."""
    action_words = set(action.lower().split())
    issue_words = set(issue.lower().split())
    # Significant overlap = related
    common = action_words & issue_words - {"the", "a", "an", "to", "is", "in", "of", "for", "and", "or"}
    return len(common) >= 2


# ── Alert → urgent task ─────────────────────────────────────────────

async def create_task_from_alert(
    session: AsyncSession,
    tenant_id: UUID,
    grow_cycle_id: UUID | None,
    tent_id: UUID | None,
    severity: str,
    alert_type: str,
    message: str,
    sensor_value: float | None = None,
) -> Task | None:
    """Create an urgent task from an alert event."""
    owner_id = await _get_tenant_owner(session, tenant_id)
    if not owner_id:
        return None

    now = datetime.now(timezone.utc)

    # Check for existing unresolved alert task with same type
    existing = (await session.execute(
        select(Task.id).where(
            Task.tenant_id == tenant_id,
            Task.category == "alert_response",
            Task.source == "auto",
            Task.status.in_(["pending", "in_progress"]),
            Task.title.contains(alert_type),
        ).limit(1)
    )).scalar_one_or_none()
    if existing:
        return None

    priority = "urgent" if severity == "critical" else "high"
    due = now if severity == "critical" else now + timedelta(hours=1)

    desc = message
    if sensor_value is not None:
        desc += f"\n\nSensor reading: {sensor_value}"

    task = Task(
        tenant_id=tenant_id,
        title=f"ALERT: {message[:480]}",
        description=desc,
        status="pending",
        priority=priority,
        category="alert_response",
        source="auto",
        created_by=owner_id,
        grow_cycle_id=grow_cycle_id,
        tent_id=tent_id,
        due_date=due,
    )
    session.add(task)
    await session.commit()
    return task


# ── Stage transition → preparation tasks ────────────────────────────

STAGE_TRANSITION_TASKS: dict[str, list[tuple[str, str, str]]] = {
    # stage: [(title, description, priority)]
    "vegetative": [
        ("Increase light hours to 18/6", "Plants are entering veg — switch light schedule to 18 on / 6 off for maximum vegetative growth.", "medium"),
        ("Begin vegetative nutrient schedule", "Transition to veg-stage nutrients. Increase nitrogen ratio for leaf and stem development.", "medium"),
    ],
    "flowering": [
        ("Switch light schedule to 12/12", "Flowering initiated — change light timer to 12 hours on / 12 hours off to trigger bloom.", "high"),
        ("Transition to bloom nutrients", "Switch from veg to bloom nutrient formula. Increase phosphorus and potassium, reduce nitrogen.", "high"),
        ("Remove male plants / check for hermies", "Inspect all plants for male pollen sacs or hermaphrodite traits. Remove immediately to protect quality.", "urgent"),
    ],
    "late_flower": [
        ("Begin daily trichome monitoring", "Use a jeweler's loupe or USB microscope to check trichome color daily. Target: mostly cloudy with 20-30% amber for peak quality.", "high"),
        ("Lower room temperature for terpene preservation", "Drop temps to 65-70°F during dark period. Cooler temps in late flower preserve terpene profiles — quality over quantity.", "high"),
        ("Reduce humidity to 40-45%", "Lower humidity to prevent bud rot and encourage resin production. Dense buds need airflow.", "high"),
    ],
    "flush": [
        ("Begin plain water flush", "Switch to plain pH'd water only. No nutrients. Goal: flush salt buildup for clean, smooth smoke.", "urgent"),
        ("Prepare harvest tools and drying space", "Gather trimming scissors, drying rack/lines, and set up a dark, 60°F/60% humidity drying room.", "medium"),
        ("Monitor runoff EC until below 0.3", "Keep flushing until runoff EC drops below 0.3 — this ensures a proper flush for the best taste.", "high"),
    ],
    "drying": [
        ("Set drying room to 60°F / 60% humidity", "Slow dry for 10-14 days produces the best results. No fans directly on buds. Dark room.", "high"),
        ("Check for mold daily during drying", "Inspect all drying branches daily for mold or rot. Remove affected areas immediately.", "high"),
    ],
    "curing": [
        ("Begin jar curing — burp jars daily", "Place dried buds in mason jars at 58-62% humidity. Open jars for 15 min daily for the first 2 weeks.", "medium"),
        ("Monitor humidity with hygrometer in jars", "Target 58-62% RH inside jars. Too high = mold risk. Too low = over-dried (add Boveda pack).", "medium"),
    ],
}


async def create_stage_transition_tasks(
    session: AsyncSession,
    grow: GrowCycle,
    new_stage: str,
) -> int:
    """Create preparation tasks when a grow transitions to a new stage."""
    tasks_for_stage = STAGE_TRANSITION_TASKS.get(new_stage, [])
    if not tasks_for_stage:
        return 0

    owner_id = await _get_tenant_owner(session, grow.tenant_id)
    if not owner_id:
        return 0

    now = datetime.now(timezone.utc)
    created = 0

    for title, description, priority in tasks_for_stage:
        # Don't duplicate
        existing = (await session.execute(
            select(Task.id).where(
                Task.grow_cycle_id == grow.id,
                Task.title == title,
                Task.status.in_(["pending", "in_progress"]),
            ).limit(1)
        )).scalar_one_or_none()
        if existing:
            continue

        task = Task(
            tenant_id=grow.tenant_id,
            title=title,
            description=description,
            status="pending",
            priority=priority,
            category="stage_transition",
            source="auto",
            created_by=owner_id,
            grow_cycle_id=grow.id,
            tent_id=grow.tent_id,
            due_date=now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1 if now.hour >= 9 else 0),
        )
        session.add(task)
        created += 1

    if created:
        await session.commit()
        logger.info("Created %d stage-transition tasks for grow %s → %s", created, grow.id, new_stage)

    return created


# ── Journal event → follow-up tasks ─────────────────────────────────

async def create_journal_followup_tasks(
    session: AsyncSession,
    tenant_id: UUID,
    grow_cycle_id: UUID | None,
    bucket_id: UUID,
    event_type: str,
    content: str | None = None,
    payload: dict | None = None,
) -> int:
    """Create follow-up tasks after journal events."""
    owner_id = await _get_tenant_owner(session, tenant_id)
    if not owner_id:
        return 0

    now = datetime.now(timezone.utc)
    created = 0
    followups: list[tuple[str, str, str, int]] = []  # (title, desc, priority, days_offset)

    if event_type == "feeding":
        followups.append((
            "Verify pH & EC stability after feeding",
            "Check pH and EC 24h after feeding to ensure no drift. Adjust if outside target range.",
            "medium",
            1,
        ))
        followups.append((
            "Check for nutrient burn (leaf tip browning)",
            "Inspect leaf tips for browning or curling — signs of overfeeding. Reduce concentration if spotted.",
            "medium",
            2,
        ))

    elif event_type == "water_change":
        followups.append((
            "Monitor pH after reservoir change",
            "Fresh water can cause pH drift in the first 12-24h. Check and adjust as needed.",
            "medium",
            1,
        ))

    elif event_type in ("training", "topping", "defoliation"):
        recovery_days = 3
        if payload and isinstance(payload, dict):
            recovery_days = payload.get("recovery_expected_days", 3)
        followups.append((
            f"Check recovery from {event_type}",
            f"Inspect plants {recovery_days} days after {event_type}. Look for healthy new growth and no wilting.",
            "medium",
            recovery_days,
        ))

    elif event_type == "transplant":
        followups.append((
            "Monitor for transplant shock",
            "Watch for drooping or yellowing in the 48h after transplant. Keep humidity high and light low if stressed.",
            "high",
            2,
        ))

    for title, desc, priority, days in followups:
        due = now + timedelta(days=days)
        due = due.replace(hour=9, minute=0, second=0, microsecond=0)

        # Don't duplicate
        existing = (await session.execute(
            select(Task.id).where(
                Task.tenant_id == tenant_id,
                Task.title == title,
                Task.status.in_(["pending", "in_progress"]),
                Task.due_date >= due - timedelta(days=1),
                Task.due_date <= due + timedelta(days=1),
            ).limit(1)
        )).scalar_one_or_none()
        if existing:
            continue

        task = Task(
            tenant_id=tenant_id,
            title=title,
            description=desc,
            status="pending",
            priority=priority,
            category="followup",
            source="auto",
            created_by=owner_id,
            grow_cycle_id=grow_cycle_id,
            bucket_id=bucket_id,
            due_date=due,
        )
        session.add(task)
        created += 1

    if created:
        await session.commit()

    return created
