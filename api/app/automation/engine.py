"""Automation rules engine — evaluates sensor readings against rules."""

from __future__ import annotations

import logging
import operator
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.models import AlertHistory, AutomationRule
from app.automation.suppression import is_suppressed, mark_fired
from app.grows.models import Bucket, BucketSensorReading

logger = logging.getLogger("tendril.automation.engine")

OPERATORS = {
    "gt": operator.gt,
    "lt": operator.lt,
    "gte": operator.ge,
    "lte": operator.le,
    "eq": operator.eq,
}

# Grow-type-specific critical alerts

# ── Trend-based alert definitions ──────────────────────────────────────────────
# Triggered when a sensor changes too fast over a time window.
# "delta" is the absolute change, "window_minutes" is the lookback period.
TREND_ALERTS: dict[str, dict] = {
    # pH drift — applies to all hydro types
    "ph_rising_fast": {
        "sensor": "ph",
        "direction": "rising",
        "delta": 0.5,
        "window_minutes": 240,
        "message": "pH rising rapidly (+{delta:.1f} in {hours:.1f}h) — check top-off water or failing pH-down dosing.",
        "severity": "warning",
        "grow_types": None,  # all types
    },
    "ph_dropping_fast": {
        "sensor": "ph",
        "direction": "falling",
        "delta": 0.5,
        "window_minutes": 240,
        "message": "pH dropping rapidly (-{delta:.1f} in {hours:.1f}h) — possible over-dose or organic acid spike.",
        "severity": "warning",
        "grow_types": None,
    },
    "ec_spiking": {
        "sensor": "ec",
        "direction": "rising",
        "delta": 0.8,
        "window_minutes": 360,
        "message": "EC spiking (+{delta:.2f} in {hours:.1f}h) — evaporation concentrating nutrients. Top off with plain water.",
        "severity": "warning",
        "grow_types": {
            "dwc",
            "rdwc",
            "nft",
            "ebb_flow",
            "kratky",
            "aeroponics",
            "aquaponics",
            "dutch_bucket",
            "vertical_tower",
        },
    },
    "ec_crashing": {
        "sensor": "ec",
        "direction": "falling",
        "delta": 0.8,
        "window_minutes": 360,
        "message": "EC dropping rapidly (-{delta:.2f} in {hours:.1f}h) — plants feeding heavily or dilution issue.",
        "severity": "info",
        "grow_types": {"dwc", "rdwc", "nft", "ebb_flow", "aeroponics", "dutch_bucket", "vertical_tower"},
    },
    "water_temp_rising": {
        "sensor": "water_temp_f",
        "direction": "rising",
        "delta": 5.0,
        "window_minutes": 120,
        "message": "Water temp rising fast (+{delta:.0f}°F in {hours:.1f}h) — check chiller/ambient cooling.",
        "severity": "warning",
        "grow_types": {"dwc", "rdwc", "nft", "ebb_flow", "aeroponics", "aquaponics", "dutch_bucket", "vertical_tower"},
    },
    "do_dropping": {
        "sensor": "dissolved_oxygen",
        "direction": "falling",
        "delta": 2.0,
        "window_minutes": 180,
        "message": "Dissolved oxygen dropping fast (-{delta:.1f} ppm in {hours:.1f}h) — air pump failing or water warming.",
        "severity": "warning",
        "grow_types": {"dwc", "rdwc", "nft", "aquaponics"},
    },
    "soil_drying_fast": {
        "sensor": "soil_moisture",
        "direction": "falling",
        "delta": 25.0,
        "window_minutes": 360,
        "message": "Soil drying rapidly (-{delta:.0f}% in {hours:.1f}h) — heat stress or undersized container.",
        "severity": "warning",
        "grow_types": {"soil", "coco", "outdoor_soil", "outdoor_container", "living_soil", "rockwool", "wicking"},
    },
}

# ── Composite multi-sensor alert definitions ───────────────────────────────────
# Triggered when multiple sensor conditions are met simultaneously.
COMPOSITE_ALERTS: list[dict] = [
    {
        "name": "root_rot_imminent",
        "conditions": [
            {"sensor": "water_temp_f", "condition": "gt", "threshold": 72},
            {"sensor": "dissolved_oxygen", "condition": "lt", "threshold": 5},
        ],
        "message": "Root rot imminent — high water temp ({water_temp_f:.0f}°F) combined with low DO ({dissolved_oxygen:.1f} ppm). Add Hydroguard + ice + increase aeration.",
        "severity": "critical",
        "grow_types": {"dwc", "rdwc", "nft", "aquaponics"},
    },
    {
        "name": "nutrient_lockout",
        "conditions": [
            {"sensor": "ph", "condition": "gt", "threshold": 7.0},
            {"sensor": "ec", "condition": "gt", "threshold": 2.5},
        ],
        "message": "Nutrient lockout likely — pH {ph:.1f} with high EC {ec:.2f}. Nutrients present but unavailable. Adjust pH to 5.8-6.2 first.",
        "severity": "warning",
        "grow_types": {"dwc", "rdwc", "nft", "ebb_flow", "drip", "aeroponics", "dutch_bucket", "vertical_tower"},
    },
    {
        "name": "salt_toxicity",
        "conditions": [
            {"sensor": "runoff_ec", "condition": "gt", "threshold": 3.5},
            {"sensor": "runoff_ph", "condition": "lt", "threshold": 5.5},
        ],
        "message": "Salt toxicity — high runoff EC ({runoff_ec:.2f}) with acidic runoff pH ({runoff_ph:.1f}). Flush with plain pH'd water until EC < 1.5.",
        "severity": "critical",
        "grow_types": {"coco", "rockwool", "drip", "dutch_bucket"},
    },
    {
        "name": "dehydration_stress",
        "conditions": [
            {"sensor": "soil_moisture", "condition": "lt", "threshold": 20},
            {"sensor": "soil_temp", "condition": "gt", "threshold": 85},
        ],
        "message": "Critical dehydration — soil dry ({soil_moisture:.0f}%) with high soil temp ({soil_temp:.0f}°F). Water immediately and provide shade.",
        "severity": "critical",
        "grow_types": {"soil", "outdoor_soil", "outdoor_container", "living_soil", "coco"},
    },
    {
        "name": "reservoir_stagnation",
        "conditions": [
            {"sensor": "water_temp_f", "condition": "gt", "threshold": 75},
            {"sensor": "ec", "condition": "gt", "threshold": 2.5},
            {"sensor": "dissolved_oxygen", "condition": "lt", "threshold": 6},
        ],
        "message": "Reservoir stagnation — warm ({water_temp_f:.0f}°F), concentrated (EC {ec:.2f}), low oxygen ({dissolved_oxygen:.1f}). Partial water change + aeration needed.",
        "severity": "warning",
        "grow_types": {"dwc", "rdwc", "kratky"},
    },
]

# ── Alert escalation config ────────────────────────────────────────────────────
# Unacknowledged alerts escalate severity after the configured hours.
ESCALATION_RULES = {
    "warning": {"escalate_to": "critical", "after_hours": 4},
    "info": {"escalate_to": "warning", "after_hours": 12},
}

# Weather-based alerts for outdoor/greenhouse
WEATHER_RULES = [
    {
        "sensor": "temperature_c",
        "condition": "lt",
        "threshold": 4,
        "message": "Frost protection needed — temperature below 4°C!",
        "severity": "critical",
        "type": "frost",
    },
    {
        "sensor": "temperature_c",
        "condition": "gt",
        "threshold": 38,
        "message": "Heat stress — temperature above 38°C!",
        "severity": "warning",
        "type": "heat",
    },
    {
        "sensor": "precipitation_mm",
        "condition": "gt",
        "threshold": 25,
        "message": "Heavy rain alert — consider covering plants!",
        "severity": "warning",
        "type": "rain",
    },
    {
        "sensor": "wind_speed_kmh",
        "condition": "gt",
        "threshold": 50,
        "message": "High wind alert — secure plants!",
        "severity": "warning",
        "type": "wind",
    },
    {
        "sensor": "uv_index",
        "condition": "gt",
        "threshold": 8,
        "message": "High UV index — consider shade for sensitive plants.",
        "severity": "info",
        "type": "uv",
    },
]

# Stage-aware threshold defaults used at evaluation time when no explicit
# per-rule stage mapping exists. This preserves current rule thresholds as the
# fallback and only tunes high-variance metrics by stage.
_STAGE_THRESHOLD_DEFAULTS: dict[str, dict[str, dict[str, float]]] = {
    "ec": {
        "seedling": {"gt": 1.4},
        "vegetative": {"gt": 1.6},
        "flowering": {"gt": 2.2},
        "ripening": {"gt": 1.6},
    },
    "runoff_ec": {
        "seedling": {"gt": 2.8},
        "vegetative": {"gt": 3.0},
        "flowering": {"gt": 3.8},
        "ripening": {"gt": 3.2},
    },
    "water_temp_f": {
        "seedling": {"gt": 72},
        "vegetative": {"gt": 72},
        "flowering": {"gt": 74},
        "ripening": {"gt": 72},
    },
    "soil_moisture": {
        "seedling": {"lt": 30},
        "vegetative": {"lt": 25},
        "flowering": {"lt": 20},
        "ripening": {"lt": 18},
    },
}


def _resolve_stage_threshold(rule: AutomationRule, stage: str | None) -> float:
    """Resolve an effective threshold using optional per-rule stage mapping.

    Resolution order:
    1) rule.action_params.stage_thresholds[stage][condition or 'threshold']
    2) built-in stage defaults for selected sensors
    3) persisted rule.threshold (current behavior fallback)
    """
    if stage:
        params = rule.action_params if isinstance(rule.action_params, dict) else {}
        stage_thresholds = params.get("stage_thresholds")
        if isinstance(stage_thresholds, dict):
            stage_entry = stage_thresholds.get(stage)
            if isinstance(stage_entry, int | float):
                return float(stage_entry)
            if isinstance(stage_entry, dict):
                by_condition = stage_entry.get(rule.condition)
                if isinstance(by_condition, int | float):
                    return float(by_condition)
                generic = stage_entry.get("threshold")
                if isinstance(generic, int | float):
                    return float(generic)

        sensor_defaults = _STAGE_THRESHOLD_DEFAULTS.get(rule.sensor, {})
        stage_defaults = sensor_defaults.get(stage, {})
        threshold = stage_defaults.get(rule.condition)
        if isinstance(threshold, int | float):
            return float(threshold)

    return rule.threshold


def _format_stage_alert_message(
    *,
    rule: AutomationRule,
    value: Any,
    threshold: float,
    stage: str | None,
) -> str:
    """Build a contextual alert message that includes stage-aware thresholding."""
    stage_label = stage or "unknown"
    return f"{rule.name} — {rule.sensor} is {value} ({rule.condition} {threshold}) for stage '{stage_label}'."


async def evaluate_rules(session: AsyncSession) -> list[AlertHistory]:
    """Evaluate all enabled automation rules against latest sensor readings.

    Returns a list of newly triggered alerts.

    Query plan
    ----------
    Previously this function ran ``1 + R + (R \u00d7 B)`` queries (one rule
    fetch, one bucket fetch per rule, one latest-reading fetch per bucket
    per rule). After PR #194 seeded 47 system-default rules per tenant
    this grew to hundreds of round trips per scheduler tick.

    The optimised path is two queries:
      1. All enabled rules (1 query).
      2. The latest ``BucketSensorReading`` per bucket for every
         ``(tenant, grow_cycle)`` pair that any rule cares about, using
         a single ``DISTINCT ON (bucket_id)`` ordered by
         ``recorded_at DESC``. Postgres reads this from the
         ``(bucket_id, recorded_at)`` index in a single sequential pass.

    Latest-reading rows are then matched in-memory against the rules.
    """
    now = datetime.now(UTC)
    triggered: list[AlertHistory] = []

    rules = (await session.execute(select(AutomationRule).where(AutomationRule.enabled.is_(True)))).scalars().all()
    if not rules:
        return triggered

    # Cooldown is cheap and lets us skip the latest-reading query entirely
    # for rules that aren't due yet. Filter before issuing query #2.
    rules = [
        rule
        for rule in rules
        if not (rule.last_triggered and (rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)) > now)
    ]
    if not rules:
        return triggered

    # Group rules by the scope they care about: either a specific
    # grow_cycle_id, or all buckets in a tenant. We issue one bucket
    # latest-reading query per distinct scope. In the common case there
    # is one scope per tenant (a few dozen buckets), so this stays at
    # ~1 query per tenant rather than scaling with the rule count.
    grow_cycle_scopes: set[tuple[object, object]] = set()  # (tenant_id, grow_cycle_id)
    tenant_scopes: set[object] = set()  # tenant_id only
    for rule in rules:
        if rule.grow_cycle_id is not None:
            grow_cycle_scopes.add((rule.tenant_id, rule.grow_cycle_id))
        else:
            tenant_scopes.add(rule.tenant_id)

    # latest_by_bucket: bucket_id -> (Bucket, latest BucketSensorReading)
    latest_by_bucket: dict[object, tuple[Bucket, BucketSensorReading]] = {}
    # buckets_for_tenant: tenant_id -> list[bucket_id] (only fully tenant-scoped rules)
    buckets_for_tenant: dict[object, list[object]] = {}
    # buckets_for_grow: grow_cycle_id -> list[bucket_id]
    buckets_for_grow: dict[object, list[object]] = {}

    async def _fetch_latest(filter_clause):
        """Run a single DISTINCT ON query and merge results into the
        ``latest_by_bucket`` map. Also returns the matched bucket rows so
        the caller can populate the per-scope lookup maps."""
        # DISTINCT ON (Bucket.id) + ORDER BY (Bucket.id, recorded_at DESC)
        # is the Postgres idiom for "latest row per group". The outer
        # ORDER BY is what makes DISTINCT ON keep the *latest* reading.
        # Buckets with no readings are still returned via the LEFT OUTER
        # JOIN, with reading columns NULL.
        stmt = (
            select(Bucket, BucketSensorReading)
            .distinct(Bucket.id)
            .outerjoin(BucketSensorReading, BucketSensorReading.bucket_id == Bucket.id)
            .where(filter_clause)
            .order_by(Bucket.id, BucketSensorReading.recorded_at.desc().nullslast())
        )
        result = await session.execute(stmt)
        matched_buckets: list[Bucket] = []
        for bucket, reading in result.all():
            matched_buckets.append(bucket)
            if reading is not None:
                latest_by_bucket[bucket.id] = (bucket, reading)
        return matched_buckets

    for tenant_id, grow_cycle_id in grow_cycle_scopes:
        bs = await _fetch_latest(Bucket.grow_cycle_id == grow_cycle_id)
        buckets_for_grow[grow_cycle_id] = [b.id for b in bs if b.tenant_id == tenant_id]

    for tenant_id in tenant_scopes:
        bs = await _fetch_latest(Bucket.tenant_id == tenant_id)
        buckets_for_tenant[tenant_id] = [b.id for b in bs]

    for rule in rules:
        op_fn = OPERATORS.get(rule.condition)
        if not op_fn:
            continue

        if rule.grow_cycle_id is not None:
            bucket_ids = buckets_for_grow.get(rule.grow_cycle_id, [])
        else:
            bucket_ids = buckets_for_tenant.get(rule.tenant_id, [])

        for bucket_id in bucket_ids:
            pair = latest_by_bucket.get(bucket_id)
            if pair is None:
                continue
            _bucket, reading = pair

            value = getattr(reading, rule.sensor, None)
            if value is None:
                continue

            if op_fn(value, rule.threshold):
                # Per-(rule, bucket) suppression — keeps multiple buckets from
                # spamming when a rule trips them all simultaneously, and
                # prevents the same bucket from re-firing within the window.
                if await is_suppressed(rule.tenant_id, rule.id, bucket_id):
                    continue

                alert = AlertHistory(
                    tenant_id=rule.tenant_id,
                    rule_id=rule.id,
                    grow_cycle_id=rule.grow_cycle_id,
                    alert_type=f"{rule.sensor}_{rule.condition}_{rule.threshold}",
                    severity=rule.severity,
                    message=f"Rule '{rule.name}': {rule.sensor} is {value} ({rule.condition} {rule.threshold})",
                    sensor_value=value,
                )
                session.add(alert)
                rule.last_triggered = now
                triggered.append(alert)
                await mark_fired(rule.tenant_id, rule.id, bucket_id)

                # Create urgent task from automation alert
                from app.scheduler.task_generator import create_task_from_alert

                try:
                    await create_task_from_alert(
                        session,
                        tenant_id=rule.tenant_id,
                        grow_cycle_id=rule.grow_cycle_id,
                        tent_id=None,
                        severity=rule.severity,
                        alert_type=f"{rule.sensor}_{rule.condition}",
                        message=f"Rule '{rule.name}': {rule.sensor} is {value} ({rule.condition} {rule.threshold})",
                        sensor_value=value,
                    )
                except Exception:
                    logger.exception("Failed to create task from rule alert")

                # Dispatch device command if rule action is a device command type
                await _dispatch_equipment_action(session, rule)

    if triggered:
        await session.commit()
        logger.info("Triggered %d automation alerts", len(triggered))

    return triggered


async def evaluate_critical_alerts(
    session: AsyncSession,
    grow_type: str,
    tenant_id,
    grow_cycle_id,
    reading: BucketSensorReading,
) -> list[AlertHistory]:
    """Evaluate grow-type-specific critical alerts for a single reading.

    Rules are loaded from the ``automation_rules`` table (seeded with
    safety-net defaults from ``critical_alerts_defaults.CRITICAL_ALERTS``).
    Tenants can disable, retune, or add to these via the standard rule
    CRUD endpoints in ``app.automation.routes``.
    """
    # Local import: avoid an import cycle between engine and service.
    from app.automation.service import list_critical_rules_query

    rules = (await session.execute(list_critical_rules_query(tenant_id=tenant_id, grow_type=grow_type))).scalars().all()
    triggered: list[AlertHistory] = []

    grow_stage: str | None = None
    if grow_cycle_id is not None:
        from app.grows.models import GrowCycle

        grow = await session.get(GrowCycle, grow_cycle_id)
        grow_stage = grow.stage if grow is not None else None

    for rule in rules:
        value = getattr(reading, rule.sensor, None)
        if value is None:
            continue

        op_fn = OPERATORS.get(rule.condition)
        if not op_fn:
            continue

        threshold = _resolve_stage_threshold(rule, grow_stage)
        if op_fn(value, threshold):
            # Per-(rule, bucket) suppression — avoids spamming when multiple
            # readings on the same bucket cross the threshold in quick
            # succession, and lets distinct buckets fire independently.
            alert_type = f"critical_{rule.sensor}_{rule.condition}_{threshold}"
            if await is_suppressed(tenant_id, alert_type, reading.bucket_id):
                continue

            alert = AlertHistory(
                tenant_id=tenant_id,
                rule_id=rule.id,
                grow_cycle_id=grow_cycle_id,
                alert_type=alert_type,
                severity=rule.severity,
                message=_format_stage_alert_message(
                    rule=rule,
                    value=value,
                    threshold=threshold,
                    stage=grow_stage,
                ),
                sensor_value=value,
            )
            session.add(alert)
            triggered.append(alert)
            await mark_fired(tenant_id, alert_type, reading.bucket_id)

    if triggered:
        await session.commit()

    return triggered


async def evaluate_trend_alerts(
    session: AsyncSession,
    grow_type: str,
    tenant_id,
    grow_cycle_id,
    bucket_id,
) -> list[AlertHistory]:
    """Detect rapid sensor changes (rate-of-change alerts).

    Compares latest reading to a reading from `window_minutes` ago.
    Returns triggered alerts.
    """
    now = datetime.now(UTC)
    triggered: list[AlertHistory] = []

    for alert_key, rule in TREND_ALERTS.items():
        # Skip if grow type doesn't match
        if rule["grow_types"] is not None and grow_type not in rule["grow_types"]:
            continue

        window = timedelta(minutes=rule["window_minutes"])
        sensor = rule["sensor"]

        # Get latest reading
        latest = (
            await session.execute(
                select(BucketSensorReading)
                .where(BucketSensorReading.bucket_id == bucket_id)
                .order_by(BucketSensorReading.recorded_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if not latest:
            continue
        current_val = getattr(latest, sensor, None)
        if current_val is None:
            continue

        # Get reading from window_minutes ago (closest to the window boundary)
        window_start = now - window
        older = (
            await session.execute(
                select(BucketSensorReading)
                .where(
                    BucketSensorReading.bucket_id == bucket_id,
                    BucketSensorReading.recorded_at <= window_start,
                )
                .order_by(BucketSensorReading.recorded_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if not older:
            continue
        older_val = getattr(older, sensor, None)
        if older_val is None:
            continue

        # Calculate delta
        actual_delta = current_val - older_val
        actual_hours = (latest.recorded_at - older.recorded_at).total_seconds() / 3600

        # Check direction and threshold
        triggered_flag = False
        if (rule["direction"] == "rising" and actual_delta >= rule["delta"]) or (
            rule["direction"] == "falling" and actual_delta <= -rule["delta"]
        ):
            triggered_flag = True

        if not triggered_flag:
            continue

        # Per-(rule, bucket) suppression — same trend on same bucket won't
        # re-fire within the window; other buckets remain independent.
        alert_type = f"trend_{alert_key}"
        if await is_suppressed(tenant_id, alert_type, bucket_id):
            continue

        message = rule["message"].format(
            delta=abs(actual_delta),
            hours=actual_hours,
        )
        alert = AlertHistory(
            tenant_id=tenant_id,
            grow_cycle_id=grow_cycle_id,
            alert_type=alert_type,
            severity=rule["severity"],
            message=message,
            sensor_value=current_val,
        )
        session.add(alert)
        triggered.append(alert)
        await mark_fired(tenant_id, alert_type, bucket_id)

    if triggered:
        await session.commit()
        logger.info("Triggered %d trend alerts for bucket %s", len(triggered), bucket_id)

    return triggered


async def evaluate_composite_alerts(
    session: AsyncSession,
    grow_type: str,
    tenant_id,
    grow_cycle_id,
    reading: BucketSensorReading,
) -> list[AlertHistory]:
    """Evaluate multi-sensor composite alerts where all conditions must be true simultaneously."""
    triggered: list[AlertHistory] = []

    for rule in COMPOSITE_ALERTS:
        # Skip if grow type doesn't match
        if grow_type not in rule["grow_types"]:
            continue

        # Check ALL conditions
        all_met = True
        sensor_values: dict[str, float] = {}
        for cond in rule["conditions"]:
            value = getattr(reading, cond["sensor"], None)
            if value is None:
                all_met = False
                break
            op_fn = OPERATORS.get(cond["condition"])
            if not op_fn or not op_fn(value, cond["threshold"]):
                all_met = False
                break
            sensor_values[cond["sensor"]] = value

        if not all_met:
            continue

        # Per-(rule, bucket) suppression — same composite on same bucket won't
        # re-fire within the window; other buckets remain independent.
        alert_type = f"composite_{rule['name']}"
        if await is_suppressed(tenant_id, alert_type, reading.bucket_id):
            continue

        message = rule["message"].format(**sensor_values)
        alert = AlertHistory(
            tenant_id=tenant_id,
            grow_cycle_id=grow_cycle_id,
            alert_type=alert_type,
            severity=rule["severity"],
            message=message,
            sensor_value=sensor_values.get(rule["conditions"][0]["sensor"]),
        )
        session.add(alert)
        triggered.append(alert)
        await mark_fired(tenant_id, alert_type, reading.bucket_id)

    if triggered:
        await session.commit()
        logger.info("Triggered %d composite alerts", len(triggered))

    return triggered


async def escalate_unacknowledged_alerts(session: AsyncSession) -> int:
    """Escalate unacknowledged alerts that have exceeded their escalation window.

    Returns count of escalated alerts.
    """
    now = datetime.now(UTC)
    escalated_count = 0

    for current_severity, rule in ESCALATION_RULES.items():
        cutoff = now - timedelta(hours=float(rule["after_hours"]))  # type: ignore[arg-type]
        stale_alerts = (
            (
                await session.execute(
                    select(AlertHistory).where(
                        AlertHistory.severity == current_severity,
                        AlertHistory.acknowledged.is_(False),
                        AlertHistory.created_at < cutoff,
                    )
                )
            )
            .scalars()
            .all()
        )

        for alert in stale_alerts:
            # Don't escalate if already superseded by a higher-severity alert of same type
            alert.severity = str(rule["escalate_to"])
            alert.message = f"[ESCALATED] {alert.message}"
            escalated_count += 1

    if escalated_count:
        await session.commit()
        logger.warning("Escalated %d unacknowledged alerts", escalated_count)

    return escalated_count


# ── Equipment Action Dispatch ──────────────────────────────────────────────────

# Actions that trigger equipment commands
_EQUIPMENT_ACTIONS = {"relay_on", "relay_off", "relay_pulse", "pump_start", "pump_stop"}


async def _dispatch_equipment_action(session: AsyncSession, rule: AutomationRule) -> None:
    """Dispatch a device command if the rule's action is a device command type.

    Reads equipment_id from rule.action_params and sends the appropriate command.
    This is additive — the alert has already been created regardless of dispatch success.
    """
    if rule.action not in _EQUIPMENT_ACTIONS:
        return

    action_params = rule.action_params or {}
    equipment_id = action_params.get("equipment_id")
    if not equipment_id:
        logger.debug("Rule %s has action %s but no equipment_id in action_params", rule.id, rule.action)
        return

    try:
        import uuid

        from app.equipment.models import ControllableEquipment
        from app.equipment.service import execute_equipment_command

        equip = await session.get(ControllableEquipment, uuid.UUID(equipment_id))
        if equip is None or equip.tenant_id != rule.tenant_id:
            logger.warning("Equipment %s not found for automation rule %s", equipment_id, rule.id)
            return

        if not equip.enabled:
            logger.info("Equipment %s is disabled, skipping automation action", equipment_id)
            return

        # Map rule action to equipment command action
        action_map = {
            "relay_on": "on",
            "relay_off": "off",
            "pump_start": "on",
            "pump_stop": "off",
        }
        command_action = action_map.get(rule.action, "on")

        success, message, _ = await execute_equipment_command(
            session=session,
            equipment=equip,
            action=command_action,
            source="automation",
        )

        if success:
            logger.info(
                "Automation rule %s dispatched %s to equipment %s: %s",
                rule.name,
                command_action,
                equip.name,
                message,
            )
        else:
            logger.warning(
                "Automation rule %s failed to dispatch %s to equipment %s: %s",
                rule.name,
                command_action,
                equip.name,
                message,
            )

    except Exception:
        logger.exception("Failed to dispatch equipment action for rule %s", rule.id)
