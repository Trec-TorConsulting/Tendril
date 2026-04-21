"""Automation rules engine — evaluates sensor readings against rules."""
from __future__ import annotations

import logging
import operator
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.models import AutomationRule, AlertHistory
from app.grows.models import BucketSensorReading, Bucket

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
        {"sensor": "flow_rate", "condition": "lt", "threshold": 0.1, "message": "NFT pump failure — flow rate critically low!", "severity": "critical"},
    ],
    "aeroponics": [
        {"sensor": "mist_pressure", "condition": "lt", "threshold": 10, "message": "Aeroponics nozzle clog — mist pressure critically low!", "severity": "critical"},
    ],
    "dwc": [
        {"sensor": "dissolved_oxygen", "condition": "lt", "threshold": 4, "message": "DWC dissolved oxygen critically low — check air pump!", "severity": "critical"},
        {"sensor": "water_temp_f", "condition": "gt", "threshold": 72, "message": "DWC water temp above 72°F — risk of root rot. Ensure Hydroguard (2 ml/gal) is dosed and air stones are running.", "severity": "warning"},
    ],
    "rdwc": [
        {"sensor": "flow_rate", "condition": "lt", "threshold": 0.1, "message": "RDWC circulation pump failure!", "severity": "critical"},
        {"sensor": "dissolved_oxygen", "condition": "lt", "threshold": 4, "message": "RDWC dissolved oxygen critically low!", "severity": "critical"},
    ],
}

# Weather-based alerts for outdoor/greenhouse
WEATHER_RULES = [
    {"sensor": "temperature_c", "condition": "lt", "threshold": 4, "message": "Frost protection needed — temperature below 4°C!", "severity": "critical", "type": "frost"},
    {"sensor": "temperature_c", "condition": "gt", "threshold": 38, "message": "Heat stress — temperature above 38°C!", "severity": "warning", "type": "heat"},
    {"sensor": "precipitation_mm", "condition": "gt", "threshold": 25, "message": "Heavy rain alert — consider covering plants!", "severity": "warning", "type": "rain"},
    {"sensor": "wind_speed_kmh", "condition": "gt", "threshold": 50, "message": "High wind alert — secure plants!", "severity": "warning", "type": "wind"},
    {"sensor": "uv_index", "condition": "gt", "threshold": 8, "message": "High UV index — consider shade for sensitive plants.", "severity": "info", "type": "uv"},
]


async def evaluate_rules(session: AsyncSession) -> list[AlertHistory]:
    """Evaluate all enabled automation rules against latest sensor readings.

    Returns a list of newly triggered alerts.
    """
    now = datetime.now(timezone.utc)
    triggered: list[AlertHistory] = []

    rules = (await session.execute(
        select(AutomationRule).where(AutomationRule.enabled.is_(True))
    )).scalars().all()

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
            buckets = (await session.execute(
                select(Bucket).where(Bucket.grow_cycle_id == rule.grow_cycle_id)
            )).scalars().all()
        else:
            buckets = (await session.execute(
                select(Bucket).where(Bucket.tenant_id == rule.tenant_id)
            )).scalars().all()

        for bucket in buckets:
            reading = (await session.execute(
                select(BucketSensorReading)
                .where(BucketSensorReading.bucket_id == bucket.id)
                .order_by(BucketSensorReading.recorded_at.desc())
                .limit(1)
            )).scalar_one_or_none()

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
            alert = AlertHistory(
                tenant_id=tenant_id,
                grow_cycle_id=grow_cycle_id,
                alert_type=f"critical_{rule['sensor']}",
                severity=rule["severity"],
                message=rule["message"],
                sensor_value=value,
            )
            session.add(alert)
            triggered.append(alert)

    if triggered:
        await session.commit()

    return triggered
