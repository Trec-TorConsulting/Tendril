"""Automation rules engine — evaluates sensor readings against rules."""

from __future__ import annotations

import logging
import operator
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.models import AlertHistory, AutomationRule
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
CRITICAL_ALERTS = {
    "nft": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.1,
            "message": "NFT pump failure — flow rate critically low!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 4.5,
            "message": "NFT pH dangerously low — roots exposed to thin film, pH accuracy critical!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 7.5,
            "message": "NFT pH dangerously high — nutrient lockout imminent!",
            "severity": "critical",
        },
    ],
    "aeroponics": [
        {
            "sensor": "mist_pressure",
            "condition": "lt",
            "threshold": 10,
            "message": "Aeroponics nozzle clog — mist pressure critically low!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 4.5,
            "message": "Aeroponics pH dangerously low — root burn imminent!",
            "severity": "critical",
        },
    ],
    "dwc": [
        {
            "sensor": "dissolved_oxygen",
            "condition": "lt",
            "threshold": 4,
            "message": "DWC dissolved oxygen critically low — check air pump!",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 72,
            "message": "DWC water temp above 72°F — risk of root rot. Ensure Hydroguard (2 ml/gal) is dosed and air stones are running.",
            "severity": "warning",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 78,
            "message": "DWC water temp critical (>78°F) — pythium risk extreme! Add ice or activate chiller immediately.",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 15,
            "message": "DWC water level critically low — roots may be exposed!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 4.5,
            "message": "DWC pH dangerously low — nutrient toxicity risk!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 7.5,
            "message": "DWC pH dangerously high — iron/calcium lockout!",
            "severity": "critical",
        },
    ],
    "rdwc": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.1,
            "message": "RDWC circulation pump failure!",
            "severity": "critical",
        },
        {
            "sensor": "dissolved_oxygen",
            "condition": "lt",
            "threshold": 4,
            "message": "RDWC dissolved oxygen critically low!",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 78,
            "message": "RDWC water temp critical (>78°F) — pythium risk extreme!",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 15,
            "message": "RDWC reservoir level critical — pump may run dry!",
            "severity": "critical",
        },
    ],
    "ebb_flow": [
        {
            "sensor": "water_level_pct",
            "condition": "gt",
            "threshold": 95,
            "message": "Ebb & Flow overflow risk — water level >95%! Check drain valve.",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 10,
            "message": "Ebb & Flow pump failure — tray not flooding!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 7.5,
            "message": "Ebb & Flow pH too high — salt buildup likely!",
            "severity": "warning",
        },
    ],
    "drip": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.05,
            "message": "Drip emitter blockage detected — flow rate near zero!",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 4.0,
            "message": "Drip runoff EC dangerously high (>4.0) — salt buildup critical! Flush immediately.",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 3.0,
            "message": "Drip runoff EC elevated (>3.0) — salt accumulation building, schedule flush.",
            "severity": "warning",
        },
    ],
    "aquaponics": [
        {
            "sensor": "dissolved_oxygen",
            "condition": "lt",
            "threshold": 5,
            "message": "Aquaponics DO critically low — fish suffocating! Check aerator immediately.",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 82,
            "message": "Aquaponics water temp >82°F — lethal for most fish species!",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "lt",
            "threshold": 55,
            "message": "Aquaponics water temp <55°F — fish metabolism dangerously low!",
            "severity": "warning",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 6.0,
            "message": "Aquaponics pH too low — harmful to fish! Target 6.8-7.2.",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 8.0,
            "message": "Aquaponics pH too high — ammonia toxicity increases with pH! Target 6.8-7.2.",
            "severity": "critical",
        },
    ],
    "dutch_bucket": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.05,
            "message": "Dutch bucket emitter blocked — one stuck emitter kills plant!",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 4.0,
            "message": "Dutch bucket runoff EC critical (>4.0) — flush bucket immediately!",
            "severity": "critical",
        },
    ],
    "vertical_tower": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.1,
            "message": "Vertical tower flow failure — top plants drying out!",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 15,
            "message": "Vertical tower reservoir low — pump may run dry!",
            "severity": "critical",
        },
    ],
    "kratky": [
        {
            "sensor": "water_level_pct",
            "condition": "gt",
            "threshold": 90,
            "message": "Kratky water level too high (>90%) — air gap eliminated, roots suffocating!",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 10,
            "message": "Kratky water level critical — roots may lose contact!",
            "severity": "warning",
        },
    ],
    "coco": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 20,
            "message": "Coco critically dry (<20%) — immediate irrigation needed!",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 4.0,
            "message": "Coco runoff EC dangerously high (>4.0) — salt toxicity! Flush with pH'd water.",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 3.0,
            "message": "Coco runoff EC elevated (>3.0) — schedule a flush soon.",
            "severity": "warning",
        },
    ],
    "rockwool": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 15,
            "message": "Rockwool slab critically dry (<15%) — immediate irrigation needed!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 85,
            "message": "Rockwool over-saturated (>85%) — root suffocation risk, skip next irrigation.",
            "severity": "warning",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 5.0,
            "message": "Rockwool runoff EC extreme (>5.0) — emergency flush required!",
            "severity": "critical",
        },
    ],
    "soil": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 15,
            "message": "Soil critically dry (<15%) — plant wilting imminent!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 85,
            "message": "Soil waterlogged (>85%) — root rot and fungus gnat risk!",
            "severity": "warning",
        },
    ],
    "living_soil": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 20,
            "message": "Living soil too dry (<20%) — microbial life dying! Water immediately (no runoff).",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 80,
            "message": "Living soil too wet (>80%) — anaerobic conditions forming, harming biology!",
            "severity": "warning",
        },
    ],
    "outdoor_soil": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 10,
            "message": "Outdoor soil critically dry (<10%) — deep water immediately!",
            "severity": "critical",
        },
    ],
    "outdoor_container": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 15,
            "message": "Outdoor container critically dry (<15%) — containers dry faster, water now!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 90,
            "message": "Outdoor container waterlogged (>90%) — check drainage holes!",
            "severity": "warning",
        },
    ],
    "wicking": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 25,
            "message": "Wicking system dry (<25%) — reservoir empty or wick disconnected!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 90,
            "message": "Wicking system over-saturated (>90%) — algae risk on wick!",
            "severity": "warning",
        },
    ],
}

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


async def evaluate_rules(session: AsyncSession) -> list[AlertHistory]:
    """Evaluate all enabled automation rules against latest sensor readings.

    Returns a list of newly triggered alerts.
    """
    now = datetime.now(UTC)
    triggered: list[AlertHistory] = []

    rules = (await session.execute(select(AutomationRule).where(AutomationRule.enabled.is_(True)))).scalars().all()

    for rule in rules:
        # Check cooldown
        if rule.last_triggered:
            cooldown_until = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
            if now < cooldown_until:
                continue

        op_fn = OPERATORS.get(rule.condition)
        if not op_fn:
            continue

        # Get latest reading for buckets in this grow cycle
        if rule.grow_cycle_id:
            buckets = (
                (await session.execute(select(Bucket).where(Bucket.grow_cycle_id == rule.grow_cycle_id)))
                .scalars()
                .all()
            )
        else:
            buckets = (await session.execute(select(Bucket).where(Bucket.tenant_id == rule.tenant_id))).scalars().all()

        for bucket in buckets:
            reading = (
                await session.execute(
                    select(BucketSensorReading)
                    .where(BucketSensorReading.bucket_id == bucket.id)
                    .order_by(BucketSensorReading.recorded_at.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()

            if not reading:
                continue

            value = getattr(reading, rule.sensor, None)
            if value is None:
                continue

            if op_fn(value, rule.threshold):
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
    """Evaluate grow-type-specific critical alerts for a single reading."""
    rules = CRITICAL_ALERTS.get(grow_type, [])
    triggered: list[AlertHistory] = []

    for rule in rules:
        value = getattr(reading, rule["sensor"], None)
        if value is None:
            continue

        op_fn = OPERATORS.get(rule["condition"])
        if not op_fn:
            continue

        if op_fn(value, rule["threshold"]):
            # Check cooldown — avoid duplicate alerts within 30 min
            alert_type = f"critical_{rule['sensor']}_{rule['condition']}_{rule['threshold']}"
            existing = (
                await session.execute(
                    select(AlertHistory)
                    .where(
                        AlertHistory.tenant_id == tenant_id,
                        AlertHistory.alert_type == alert_type,
                        AlertHistory.created_at > datetime.now(UTC) - timedelta(minutes=30),
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
            if existing:
                continue

            alert = AlertHistory(
                tenant_id=tenant_id,
                grow_cycle_id=grow_cycle_id,
                alert_type=alert_type,
                severity=rule["severity"],
                message=rule["message"],
                sensor_value=value,
            )
            session.add(alert)
            triggered.append(alert)

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

        # Cooldown: don't fire same trend alert within the window period
        alert_type = f"trend_{alert_key}"
        existing = (
            await session.execute(
                select(AlertHistory)
                .where(
                    AlertHistory.tenant_id == tenant_id,
                    AlertHistory.alert_type == alert_type,
                    AlertHistory.created_at > now - window,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing:
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

        # Cooldown: 1 hour for composite alerts
        alert_type = f"composite_{rule['name']}"
        existing = (
            await session.execute(
                select(AlertHistory)
                .where(
                    AlertHistory.tenant_id == tenant_id,
                    AlertHistory.alert_type == alert_type,
                    AlertHistory.created_at > datetime.now(UTC) - timedelta(hours=1),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing:
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
        cutoff = now - timedelta(hours=rule["after_hours"])
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
            alert.severity = rule["escalate_to"]
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
