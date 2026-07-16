"""Scheduler task definitions."""

from __future__ import annotations

import asyncio
import base64
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.config import Settings
from app.scheduler.health import record_task_error, record_task_run, record_vision_auto_scan_stats

logger = logging.getLogger("tendril.scheduler.tasks")

_COACHING_DEFAULTS = {
    "enabled": True,
    "cadence_hours": 24,
    "minimum_severity": "info",
}
_VISION_SCAN_DEFAULTS = {
    "enabled": True,
    "cadence_minutes": 60,
    "confidence_task_threshold": 0.9,
    "task_cooldown_hours": 12,
}
_SEVERITY_RANK = {"info": 1, "warning": 2, "critical": 3}


def _normalize_coaching_settings(raw: dict | None) -> dict[str, bool | int | str]:
    data = raw if isinstance(raw, dict) else {}
    enabled = bool(data.get("enabled", _COACHING_DEFAULTS["enabled"]))
    cadence = data.get("cadence_hours", _COACHING_DEFAULTS["cadence_hours"])
    minimum = data.get("minimum_severity", _COACHING_DEFAULTS["minimum_severity"])

    cadence_hours = cadence if isinstance(cadence, int) and 1 <= cadence <= 168 else 24
    minimum_severity = minimum if minimum in _SEVERITY_RANK else "info"

    return {
        "enabled": enabled,
        "cadence_hours": cadence_hours,
        "minimum_severity": minimum_severity,
    }


def _severity_allowed(alert_severity: str, minimum_severity: str) -> bool:
    return _SEVERITY_RANK.get(alert_severity, 0) >= _SEVERITY_RANK.get(minimum_severity, 1)


def _normalize_vision_scan_settings(raw: dict | None) -> dict[str, bool | int | float]:
    data = raw if isinstance(raw, dict) else {}
    enabled = bool(data.get("enabled", _VISION_SCAN_DEFAULTS["enabled"]))

    cadence = data.get("cadence_minutes", _VISION_SCAN_DEFAULTS["cadence_minutes"])
    cadence_minutes = cadence if isinstance(cadence, int) and 15 <= cadence <= 1440 else 60

    threshold = data.get("confidence_task_threshold", _VISION_SCAN_DEFAULTS["confidence_task_threshold"])
    if isinstance(threshold, int | float) and 0.5 <= float(threshold) <= 1.0:
        confidence_task_threshold = float(threshold)
    else:
        confidence_task_threshold = 0.9

    cooldown = data.get("task_cooldown_hours", _VISION_SCAN_DEFAULTS["task_cooldown_hours"])
    task_cooldown_hours = cooldown if isinstance(cooldown, int) and 1 <= cooldown <= 168 else 12

    return {
        "enabled": enabled,
        "cadence_minutes": cadence_minutes,
        "confidence_task_threshold": confidence_task_threshold,
        "task_cooldown_hours": task_cooldown_hours,
    }


def _merge_vision_scan_settings(
    *,
    tenant_settings: dict | None,
    grow_settings: dict | None,
) -> dict[str, bool | int | float]:
    merged = _normalize_vision_scan_settings(tenant_settings)
    if isinstance(grow_settings, dict):
        for key in (
            "enabled",
            "cadence_minutes",
            "confidence_task_threshold",
            "task_cooldown_hours",
        ):
            if key in grow_settings:
                validated = _normalize_vision_scan_settings({key: grow_settings[key]})
                merged[key] = validated[key]
    return merged


# Task intervals in seconds
HEALTH_CHECK_INTERVAL = 12 * 3600  # 12 hours
WEATHER_POLL_INTERVAL = 30 * 60  # 30 minutes
ALERT_EVAL_INTERVAL = 60  # 1 minute
RULE_EVAL_INTERVAL = 30  # 30 seconds
RETENTION_INTERVAL = 24 * 3600  # Daily
DAILY_REPORT_INTERVAL = 24 * 3600  # Daily
HARVEST_CHECK_INTERVAL = 4 * 3600  # 4 hours
TASK_GENERATION_INTERVAL = 6 * 3600  # 6 hours
PROACTIVE_COACHING_INTERVAL = 6 * 3600  # 6 hours
INTEGRATION_POLL_INTERVAL = 60  # 1 minute (checks due integrations)
DUNNING_CHECK_INTERVAL = 3600  # Hourly
ACCOUNT_PURGE_INTERVAL = 24 * 3600  # Daily
PLAN_RECONCILE_INTERVAL = 6 * 3600  # Every 6 hours
VISION_SCAN_LOOP_INTERVAL = 5 * 60  # Evaluate cadence every 5 minutes


class TaskRunner:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._vision_last_scan_at: dict[UUID, datetime] = {}

    async def run(self, shutdown_event: asyncio.Event) -> None:
        """Run all scheduled tasks until shutdown."""
        tasks = [
            asyncio.create_task(self._loop(shutdown_event, "health_check", HEALTH_CHECK_INTERVAL, self._health_check)),
            asyncio.create_task(self._loop(shutdown_event, "weather_poll", WEATHER_POLL_INTERVAL, self._weather_poll)),
            asyncio.create_task(self._loop(shutdown_event, "alert_eval", ALERT_EVAL_INTERVAL, self._alert_eval)),
            asyncio.create_task(self._loop(shutdown_event, "rule_eval", RULE_EVAL_INTERVAL, self._rule_eval)),
            asyncio.create_task(self._loop(shutdown_event, "retention", RETENTION_INTERVAL, self._data_retention)),
            asyncio.create_task(self._loop(shutdown_event, "daily_report", DAILY_REPORT_INTERVAL, self._daily_report)),
            asyncio.create_task(
                self._loop(shutdown_event, "harvest_check", HARVEST_CHECK_INTERVAL, self._harvest_countdown_check)
            ),
            asyncio.create_task(
                self._loop(shutdown_event, "task_generation", TASK_GENERATION_INTERVAL, self._generate_tasks)
            ),
            asyncio.create_task(
                self._loop(
                    shutdown_event,
                    "proactive_coaching",
                    PROACTIVE_COACHING_INTERVAL,
                    self._proactive_coaching,
                )
            ),
            asyncio.create_task(
                self._loop(shutdown_event, "integration_poll", INTEGRATION_POLL_INTERVAL, self._integration_poll)
            ),
            asyncio.create_task(
                self._loop(shutdown_event, "dunning_check", DUNNING_CHECK_INTERVAL, self._dunning_check)
            ),
            asyncio.create_task(
                self._loop(shutdown_event, "account_purge", ACCOUNT_PURGE_INTERVAL, self._account_purge)
            ),
            asyncio.create_task(
                self._loop(shutdown_event, "plan_reconcile", PLAN_RECONCILE_INTERVAL, self._plan_reconcile)
            ),
            asyncio.create_task(
                self._loop(shutdown_event, "vision_auto_scan", VISION_SCAN_LOOP_INTERVAL, self._vision_auto_scan)
            ),
        ]
        await shutdown_event.wait()
        for t in tasks:
            t.cancel()

    async def _vision_auto_scan(self) -> None:
        """Run scheduled vision scans for active grows that have a camera configured."""
        from sqlalchemy import and_, select

        from app.commercial.models import Task
        from app.database import async_session_factory
        from app.grows.models import GrowCycle, Tent, TentCamera, VisionDetection
        from app.grows.tent_routes import _fetch_camera_image
        from app.tenants.models import Tenant, TenantMembership, TenantRole
        from app.vision.client import VisionDetectorClient
        from app.vision.contracts import VisionProfile

        client = VisionDetectorClient.from_settings()
        now = datetime.now(UTC)

        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(GrowCycle, Tent, Tenant)
                    .join(Tent, GrowCycle.tent_id == Tent.id)
                    .join(Tenant, GrowCycle.tenant_id == Tenant.id)
                    .where(
                        and_(
                            GrowCycle.status == "active",
                            GrowCycle.deleted_at.is_(None),
                            Tent.deleted_at.is_(None),
                        )
                    )
                )
                rows = result.all()

                if not rows:
                    logger.debug("No active grows for scheduled vision scan")
                    return

                saved_detections = 0
                scanned_grows = 0
                skipped_grows = 0
                failed_grows = 0
                tasks_created = 0
                owner_cache: dict[UUID, UUID] = {}

                for grow, tent, tenant in rows:
                    tenant_cfg_raw = tenant.coaching_settings if isinstance(tenant.coaching_settings, dict) else {}
                    tenant_scan_cfg = tenant_cfg_raw.get("vision_auto_scan") if isinstance(tenant_cfg_raw, dict) else {}

                    grow_cfg_raw = grow.settings if isinstance(grow.settings, dict) else {}
                    grow_scan_cfg = grow_cfg_raw.get("vision_auto_scan") if isinstance(grow_cfg_raw, dict) else {}

                    scan_cfg = _merge_vision_scan_settings(
                        tenant_settings=tenant_scan_cfg,
                        grow_settings=grow_scan_cfg,
                    )
                    if not bool(scan_cfg["enabled"]):
                        skipped_grows += 1
                        continue

                    last_scan = self._vision_last_scan_at.get(grow.id)
                    cadence_minutes = int(scan_cfg["cadence_minutes"])
                    if last_scan and (now - last_scan) < timedelta(minutes=cadence_minutes):
                        skipped_grows += 1
                        continue

                    try:
                        camera_result = await session.execute(
                            select(TentCamera)
                            .where(TentCamera.tent_id == tent.id, TentCamera.is_primary.is_(True))
                            .limit(1)
                        )
                        camera = camera_result.scalar_one_or_none()

                        camera_url = camera.url if camera else tent.camera_url
                        camera_type = camera.camera_type if camera else "http_snapshot"
                        if not camera_url:
                            skipped_grows += 1
                            continue

                        image_bytes = await _fetch_camera_image(camera_url, camera_type)
                        image_b64 = base64.b64encode(image_bytes).decode("ascii")

                        model_response = await client.scan_image(
                            image_base64=image_b64,
                            profile=VisionProfile.CONTINUOUS_SCAN,
                            source="scheduled",
                            source_ref=str(tent.id),
                        )
                        scanned_grows += 1
                        self._vision_last_scan_at[grow.id] = now

                        if model_response.model_version is None:
                            continue

                        detections = [
                            VisionDetection(
                                tenant_id=grow.tenant_id,
                                grow_cycle_id=grow.id,
                                source="scheduled",
                                source_ref=str(tent.id),
                                image_storage_key=None,
                                class_name=item.class_name,
                                confidence=item.confidence,
                                bbox=item.bbox.as_list(),
                                model_version=model_response.model_version,
                                accelerator_tier=model_response.accelerator_tier.value,
                            )
                            for item in model_response.detections
                        ]

                        if detections:
                            session.add_all(detections)
                            saved_detections += len(detections)

                            threshold = float(scan_cfg["confidence_task_threshold"])
                            high_conf = [d for d in detections if float(d.confidence) >= threshold]
                            if high_conf:
                                owner_id = owner_cache.get(grow.tenant_id)
                                if owner_id is None:
                                    owner_result = await session.execute(
                                        select(TenantMembership.user_id)
                                        .where(
                                            TenantMembership.tenant_id == grow.tenant_id,
                                            TenantMembership.role == TenantRole.admin,
                                        )
                                        .limit(1)
                                    )
                                    owner_id = owner_result.scalar_one_or_none()
                                    if owner_id is not None:
                                        owner_cache[grow.tenant_id] = owner_id

                                if owner_id is not None:
                                    cooldown_hours = int(scan_cfg["task_cooldown_hours"])
                                    cutoff = now - timedelta(hours=cooldown_hours)
                                    existing_task_result = await session.execute(
                                        select(Task.id)
                                        .where(
                                            Task.tenant_id == grow.tenant_id,
                                            Task.grow_cycle_id == grow.id,
                                            Task.category == "vision_alert",
                                            Task.status.in_(["pending", "in_progress"]),
                                            Task.created_at >= cutoff,
                                        )
                                        .limit(1)
                                    )
                                    if existing_task_result.scalar_one_or_none() is None:
                                        max_conf = max(float(d.confidence) for d in high_conf)
                                        priority = "high" if max_conf >= 0.95 else "medium"
                                        classes = sorted({d.class_name for d in high_conf})
                                        summary = ", ".join(classes[:4])
                                        if len(classes) > 4:
                                            summary = f"{summary}, +{len(classes) - 4} more"

                                        task = Task(
                                            tenant_id=grow.tenant_id,
                                            title="Review automatic TPU vision detections",
                                            description=(
                                                f"Scheduled scan detected: {summary}. Top confidence: {max_conf:.2f}."
                                            ),
                                            status="pending",
                                            priority=priority,
                                            category="vision_alert",
                                            source="auto",
                                            created_by=owner_id,
                                            grow_cycle_id=grow.id,
                                            tent_id=grow.tent_id,
                                            due_date=now,
                                            routine="on_demand",
                                            estimated_minutes=10,
                                        )
                                        session.add(task)
                                        tasks_created += 1

                            await session.commit()
                    except Exception:
                        failed_grows += 1
                        logger.exception("Scheduled vision scan failed for grow %s", grow.id)

                record_vision_auto_scan_stats(
                    scanned=scanned_grows,
                    skipped=skipped_grows,
                    failed=failed_grows,
                    detections=saved_detections,
                    tasks_created=tasks_created,
                )

                logger.info(
                    (
                        "Scheduled vision scans complete: scanned=%d skipped=%d "
                        "failed=%d saved_detections=%d tasks_created=%d"
                    ),
                    scanned_grows,
                    skipped_grows,
                    failed_grows,
                    saved_detections,
                    tasks_created,
                )
        except Exception:
            logger.exception("Vision auto-scan task failed")

    async def _loop(
        self,
        shutdown_event: asyncio.Event,
        name: str,
        interval: float,
        func,
    ) -> None:
        error_retry_delay = min(interval, 300)  # Retry after 5 min on error (capped at interval)
        while not shutdown_event.is_set():
            failed = False
            try:
                await func()
                record_task_run()
            except Exception:
                logger.exception("Error in task %s", name)
                record_task_error(name)
                failed = True
            wait = error_retry_delay if failed else interval
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=wait)
                break
            except TimeoutError:
                pass

    async def _health_check(self) -> None:
        """Run Gemini health checks for active grows with auto_health_check enabled.

        Uses full grow data (sensors, trends, feeding, journal, camera) for maximum detail.
        """
        from sqlalchemy import desc, select

        from app.ai.context import build_health_check_prompt
        from app.ai.gather import gather_grow_data
        from app.ai.gemini import GeminiRateLimitError
        from app.ai.gemini import chat_completion as gemini_chat
        from app.ai.gemini import is_configured as gemini_configured
        from app.database import async_session_factory
        from app.grows.models import GrowCycle, HealthEval

        if not gemini_configured():
            logger.warning("Gemini API key not configured — skipping scheduled health checks")
            return

        try:
            async with async_session_factory() as session:
                grows = (
                    (
                        await session.execute(
                            select(GrowCycle).where(
                                GrowCycle.status == "active",
                                GrowCycle.auto_health_check.is_(True),
                            )
                        )
                    )
                    .scalars()
                    .all()
                )

                if not grows:
                    logger.debug("No active grows with auto_health_check enabled")
                    return

                for grow in grows:
                    try:
                        # Check if last eval is recent enough (skip if < 11h to avoid drift)
                        prev = (
                            await session.execute(
                                select(HealthEval)
                                .where(HealthEval.grow_cycle_id == grow.id)
                                .order_by(desc(HealthEval.created_at))
                                .limit(1)
                            )
                        ).scalar_one_or_none()

                        if prev:
                            from datetime import datetime

                            age_hours = (datetime.now(UTC) - prev.created_at).total_seconds() / 3600
                            if age_hours < 11:
                                logger.debug("Grow %s last eval %.1fh ago — skipping", grow.id, age_hours)
                                continue

                        # Gather ALL data including camera snapshot
                        grow_data = await gather_grow_data(
                            session,
                            grow,
                            include_camera=True,
                        )

                        observations = {"automated_check": "Scheduled 12-hour health check"}
                        messages = await build_health_check_prompt(grow_data, observations, session=session)

                        camera_image: bytes | None = grow_data.get("camera_image")
                        raw = await gemini_chat(messages, image_bytes=camera_image)

                        # Parse result
                        import json

                        score = None
                        issues: list[str] = []
                        actions: list[str] = []
                        try:
                            cleaned = raw.strip()
                            if cleaned.startswith("```"):
                                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
                            if cleaned.endswith("```"):
                                cleaned = cleaned[:-3]
                            cleaned = cleaned.strip()
                            parsed = json.loads(cleaned)
                            score = parsed.get("score")
                            raw_issues = parsed.get("issues", [])
                            raw_actions = parsed.get("actions", [])
                            # Normalize: AI may return list[dict] or list[str]
                            issues = []
                            for i in raw_issues:
                                if isinstance(i, str):
                                    issues.append(i)
                                else:
                                    description = i.get("description") or i.get("message") or i.get("issue") or str(i)
                                    cat = i.get("category")
                                    issues.append(f"[{cat}] {description}" if cat else description)
                            actions = [
                                a
                                if isinstance(a, str)
                                else (a.get("action") or a.get("message") or a.get("description") or str(a))
                                for a in raw_actions
                            ]
                        except json.JSONDecodeError:
                            logger.warning("Gemini returned non-JSON for grow %s", grow.id)

                        # Store
                        health_eval = HealthEval(
                            tenant_id=grow.tenant_id,
                            grow_cycle_id=grow.id,
                            score=score,
                            issues=issues,
                            actions=actions,
                            raw_analysis=raw,
                            source="scheduled",
                        )
                        session.add(health_eval)

                        # Invalidate cached feeding advice so next request regenerates
                        grow.cached_feeding_advice = None
                        grow.feeding_advice_cached_at = None

                        # Save camera snapshot as a grow photo for timelapse / gallery
                        if camera_image:
                            try:
                                from app.grows.models import GrowPhoto
                                from app.storage import upload_photo as s3_upload

                                key = await asyncio.get_running_loop().run_in_executor(
                                    None,
                                    s3_upload,
                                    camera_image,
                                    "image/jpeg",
                                    str(grow.tenant_id),
                                    str(grow.id),
                                )
                                session.add(
                                    GrowPhoto(
                                        tenant_id=grow.tenant_id,
                                        grow_cycle_id=grow.id,
                                        source="health_check",
                                        storage_key=key,
                                        caption=f"Scheduled snapshot (score: {score})"
                                        if score
                                        else "Scheduled snapshot",
                                    )
                                )
                            except Exception:
                                logger.exception("Failed to save scheduled snapshot to S3 for grow %s", grow.id)

                        await session.commit()

                        # ── Create tasks from health eval actions ──
                        if actions:
                            from app.scheduler.task_generator import create_tasks_from_health_eval

                            try:
                                task_count = await create_tasks_from_health_eval(
                                    session,
                                    grow,
                                    score,
                                    issues,
                                    actions,
                                )
                                if task_count:
                                    logger.info("Created %d tasks from health eval for grow %s", task_count, grow.id)
                            except Exception:
                                logger.exception("Failed to create tasks from health eval for grow %s", grow.id)

                        logger.info("Scheduled health check for grow %s: score=%s", grow.id, score)
                    except GeminiRateLimitError:
                        logger.warning("Gemini rate limit during scheduled check for grow %s — stopping batch", grow.id)
                        break
                    except Exception:
                        logger.exception("Scheduled health check failed for grow %s", grow.id)

                logger.info("Scheduled health checks completed for %d eligible grows", len(grows))
        except Exception:
            logger.exception("Health check task failed")

    async def _weather_poll(self) -> None:
        """Fetch weather for outdoor/greenhouse tents and store readings."""
        from sqlalchemy import select

        from app.database import async_session_factory
        from app.grows.models import Tent, WeatherReading
        from app.weather.client import fetch_weather

        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(Tent).where(
                        Tent.environment_type.in_(["outdoor", "greenhouse"]),
                        Tent.latitude.isnot(None),
                        Tent.longitude.isnot(None),
                    )
                )
                tents = result.scalars().all()

                for tent in tents:
                    try:
                        assert tent.latitude is not None and tent.longitude is not None
                        data = await fetch_weather(tent.latitude, tent.longitude)
                        current = data["current"]
                        reading = WeatherReading(
                            tenant_id=tent.tenant_id,
                            tent_id=tent.id,
                            temperature_c=current.get("temperature_c"),
                            humidity_pct=current.get("humidity_pct"),
                            precipitation_mm=current.get("precipitation_mm"),
                            wind_speed_kmh=current.get("wind_speed_kmh"),
                            uv_index=current.get("uv_index"),
                            weather_code=current.get("weather_code"),
                            dew_point_c=current.get("dew_point_c"),
                            pressure_hpa=current.get("pressure_hpa"),
                            soil_temp_c=current.get("soil_temp_c"),
                            forecast=data.get("forecast"),
                            source="open_meteo",
                        )
                        session.add(reading)
                    except Exception:
                        logger.exception("Weather fetch failed for tent %s", tent.id)

                await session.commit()
                logger.info("Weather poll completed for %d tents", len(tents))
        except Exception:
            logger.exception("Weather poll failed")

    async def _alert_eval(self) -> None:
        """Evaluate weather-based alerts for outdoor/greenhouse tents."""
        from datetime import timedelta

        from sqlalchemy import desc, select

        from app.automation.engine import OPERATORS, WEATHER_RULES
        from app.automation.models import AlertHistory
        from app.database import async_session_factory
        from app.grows.models import Tent, WeatherReading

        try:
            async with async_session_factory() as session:
                tents = (
                    (
                        await session.execute(
                            select(Tent).where(
                                Tent.environment_type.in_(["outdoor", "greenhouse"]),
                            )
                        )
                    )
                    .scalars()
                    .all()
                )

                for tent in tents:
                    w = (
                        await session.execute(
                            select(WeatherReading)
                            .where(WeatherReading.tent_id == tent.id)
                            .order_by(desc(WeatherReading.recorded_at))
                            .limit(1)
                        )
                    ).scalar_one_or_none()
                    if not w:
                        continue

                    for rule in WEATHER_RULES:
                        value = getattr(w, str(rule["sensor"]), None)
                        if value is None:
                            continue
                        op_fn = OPERATORS.get(str(rule["condition"]))
                        if op_fn and op_fn(value, float(rule["threshold"])):  # type: ignore[arg-type]
                            # Check if alert already fired recently (1h cooldown)
                            from datetime import datetime

                            cutoff = datetime.now(UTC) - timedelta(hours=1)
                            existing = (
                                await session.execute(
                                    select(AlertHistory).where(
                                        AlertHistory.tenant_id == tent.tenant_id,
                                        AlertHistory.alert_type == f"weather_{rule['type']}",
                                        AlertHistory.created_at > cutoff,
                                    )
                                )
                            ).scalar_one_or_none()
                            if existing:
                                continue

                            alert = AlertHistory(
                                tenant_id=tent.tenant_id,
                                alert_type=f"weather_{rule['type']}",
                                severity=rule["severity"],
                                message=rule["message"],
                                sensor_value=value,
                            )
                            session.add(alert)

                            # Create urgent task from weather alert
                            # Find active grow for this tent
                            from app.grows.models import GrowCycle
                            from app.scheduler.task_generator import create_task_from_alert

                            active_grow = (
                                await session.execute(
                                    select(GrowCycle)
                                    .where(GrowCycle.tent_id == tent.id, GrowCycle.status == "active")
                                    .limit(1)
                                )
                            ).scalar_one_or_none()
                            try:
                                await create_task_from_alert(
                                    session,
                                    tenant_id=tent.tenant_id,
                                    grow_cycle_id=active_grow.id if active_grow else None,
                                    tent_id=tent.id,
                                    severity=str(rule["severity"]),
                                    alert_type=f"weather_{rule['type']}",
                                    message=str(rule["message"]),
                                    sensor_value=value,
                                )
                            except Exception:
                                logger.exception("Failed to create task from weather alert")

                            # Dispatch notification
                            from app.notifications.service import dispatch_alert

                            await dispatch_alert(
                                session,
                                tent.tenant_id,
                                str(rule["severity"]),
                                f"Weather Alert: {rule['type']}",
                                str(rule["message"]),
                            )

                await session.commit()
        except Exception:
            logger.exception("Alert eval task failed")

    async def _rule_eval(self) -> None:
        """Evaluate automation rules, trend alerts, composite alerts, and escalation."""
        from app.automation.engine import (
            escalate_unacknowledged_alerts,
            evaluate_rules,
        )
        from app.database import async_session_factory

        try:
            async with async_session_factory() as session:
                triggered = await evaluate_rules(session)
                if triggered:
                    logger.info("Rule eval triggered %d alerts", len(triggered))

                # Escalate stale unacknowledged alerts
                escalated = await escalate_unacknowledged_alerts(session)
                if escalated:
                    logger.info("Escalated %d unacknowledged alerts", escalated)
        except Exception:
            logger.exception("Rule eval task failed")

    async def _daily_report(self) -> None:
        """Generate daily grow reports and dispatch notifications."""
        from sqlalchemy import select

        from app.ai.reports import generate_grow_report
        from app.database import async_session_factory
        from app.grows.models import GrowCycle
        from app.notifications.service import dispatch_alert

        try:
            async with async_session_factory() as session:
                grows = (await session.execute(select(GrowCycle).where(GrowCycle.status == "active"))).scalars().all()

                for grow in grows:
                    try:
                        await generate_grow_report(session, grow.id)
                        logger.info("Daily report generated for grow %s", grow.id)
                    except Exception:
                        logger.exception("Daily report failed for grow %s", grow.id)

                # Send daily digest notification per tenant
                tenant_ids = {g.tenant_id for g in grows}
                for tid in tenant_ids:
                    grow_count = sum(1 for g in grows if g.tenant_id == tid)
                    await dispatch_alert(
                        session,
                        tid,
                        "info",
                        "Daily Grow Report",
                        f"Daily health reports generated for {grow_count} active grow(s).",
                    )

                logger.info("Daily reports completed for %d grows", len(grows))
        except Exception:
            logger.exception("Daily report task failed")

    async def _data_retention(self) -> None:
        """Prune old sensor data per tenant retention settings."""
        from app.data.service import enforce_retention
        from app.database import async_session_factory

        try:
            async with async_session_factory() as session:
                deleted = await enforce_retention(session)
                total = sum(deleted.values())
                if total > 0:
                    logger.info("Data retention pruned %d rows: %s", total, deleted)
                else:
                    logger.debug("Data retention: nothing to prune")
        except Exception:
            logger.exception("Data retention task failed")

    async def _harvest_countdown_check(self) -> None:
        """Check harvest windows and send countdown notifications.

        Alerts at 7 days, 3 days, and 0 days (harvest day) before estimated harvest.
        """
        from datetime import datetime, timedelta

        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.automation.models import AlertHistory
        from app.database import async_session_factory
        from app.grows.models import Bucket, GrowCycle
        from app.notifications.service import dispatch_alert

        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(GrowCycle)
                    .options(selectinload(GrowCycle.buckets).selectinload(Bucket.strain))
                    .where(GrowCycle.status == "active")
                )
                grows = result.scalars().all()
                now = datetime.now(UTC)

                for grow in grows:
                    milestones = grow.milestones or {}
                    flowering_start_str = milestones.get("flowering") or milestones.get("flower")
                    if not flowering_start_str:
                        continue

                    flowering_start = datetime.fromisoformat(flowering_start_str)
                    if flowering_start.tzinfo is None:
                        flowering_start = flowering_start.replace(tzinfo=UTC)

                    for bucket in grow.buckets:
                        if bucket.status != "active":
                            continue
                        strain = bucket.strain
                        if not strain or not strain.flowering_days:
                            continue

                        estimated_harvest = flowering_start + timedelta(days=strain.flowering_days)
                        days_remaining = (estimated_harvest - now).days

                        # Alert thresholds
                        for threshold in (7, 3, 0):
                            if days_remaining > threshold or days_remaining < threshold - 1:
                                continue

                            alert_type = f"harvest_{threshold}d_{bucket.id}"
                            # Check cooldown (24h per alert type)
                            cutoff = now - timedelta(hours=24)
                            existing = (
                                await session.execute(
                                    select(AlertHistory).where(
                                        AlertHistory.tenant_id == grow.tenant_id,
                                        AlertHistory.alert_type == alert_type,
                                        AlertHistory.created_at > cutoff,
                                    )
                                )
                            ).scalar_one_or_none()
                            if existing:
                                continue

                            if threshold == 0:
                                severity = "critical"
                                title = "Harvest Day!"
                                msg = (
                                    f"🌿 {strain.name} in '{grow.name}' "
                                    f"(bucket {bucket.label or bucket.position}) has reached its "
                                    f"estimated harvest window ({strain.flowering_days} flowering days)."
                                )
                            elif threshold == 3:
                                severity = "warning"
                                title = "Harvest in 3 Days"
                                msg = (
                                    f"🌿 {strain.name} in '{grow.name}' "
                                    f"(bucket {bucket.label or bucket.position}) — estimated harvest "
                                    f"in ~{days_remaining} days. Begin final flush preparations."
                                )
                            else:
                                severity = "info"
                                title = "Harvest in 7 Days"
                                msg = (
                                    f"🌿 {strain.name} in '{grow.name}' "
                                    f"(bucket {bucket.label or bucket.position}) — estimated harvest "
                                    f"in ~{days_remaining} days. Consider starting flush soon."
                                )

                            alert = AlertHistory(
                                tenant_id=grow.tenant_id,
                                alert_type=alert_type,
                                severity=severity,
                                message=msg,
                            )
                            session.add(alert)
                            await dispatch_alert(session, grow.tenant_id, severity, title, msg)
                            logger.info(
                                "Harvest alert: %s for grow %s bucket %s (%dd)",
                                title,
                                grow.id,
                                bucket.id,
                                days_remaining,
                            )

                await session.commit()
                logger.debug("Harvest countdown check completed for %d grows", len(grows))
        except Exception:
            logger.exception("Harvest countdown check failed")

    async def _generate_tasks(self) -> None:
        """Auto-generate grow tasks based on grow type, stage, and strain data."""
        from app.database import async_session_factory
        from app.scheduler.task_generator import generate_all_tasks

        try:
            async with async_session_factory() as session:
                count = await generate_all_tasks(session)
                if count:
                    logger.info("Auto-generated %d tasks", count)
                else:
                    logger.debug("Task generation: no new tasks needed")
        except Exception:
            logger.exception("Task generation failed")

    async def _proactive_coaching(self) -> None:
        """Emit low-noise proactive coaching nudges with per-grow cooldown."""
        from datetime import datetime, timedelta

        from sqlalchemy import desc, select

        from app.automation.models import AlertHistory
        from app.database import async_session_factory
        from app.grows.models import GrowCycle, HealthEval
        from app.notifications.service import dispatch_alert
        from app.tenants.models import Tenant

        try:
            async with async_session_factory() as session:
                grows = (await session.execute(select(GrowCycle).where(GrowCycle.status == "active"))).scalars().all()
                if not grows:
                    logger.debug("Proactive coaching: no active grows")
                    return

                tenant_ids = {g.tenant_id for g in grows}
                settings_rows = (
                    await session.execute(select(Tenant.id, Tenant.coaching_settings).where(Tenant.id.in_(tenant_ids)))
                ).all()
                coaching_by_tenant = {tenant_id: _normalize_coaching_settings(raw) for tenant_id, raw in settings_rows}

                now = datetime.now(UTC)

                for grow in grows:
                    settings = coaching_by_tenant.get(grow.tenant_id, _COACHING_DEFAULTS)
                    if not bool(settings["enabled"]):
                        continue
                    cadence_hours = int(settings["cadence_hours"])
                    minimum_severity = str(settings["minimum_severity"])
                    cutoff = now - timedelta(hours=cadence_hours)

                    latest_eval = (
                        await session.execute(
                            select(HealthEval)
                            .where(HealthEval.grow_cycle_id == grow.id)
                            .order_by(desc(HealthEval.created_at))
                            .limit(1)
                        )
                    ).scalar_one_or_none()

                    alert_type: str | None = None
                    severity = "info"
                    title: str | None = None
                    message: str | None = None

                    if latest_eval is None or latest_eval.created_at < cutoff:
                        alert_type = f"coaching_healthcheck_{grow.id}"
                        title = "Quick Health Check Recommended"
                        message = (
                            f"No recent AI health check was found for '{grow.name}'. "
                            "Run a check now to refresh recommendations and catch issues early."
                        )
                    elif latest_eval.score is not None and latest_eval.score <= 60:
                        alert_type = f"coaching_low_health_{grow.id}"
                        severity = "warning"
                        title = "Low Health Score Follow-Up"
                        message = (
                            f"'{grow.name}' recently scored {latest_eval.score}/100. "
                            "Focus on pending critical tasks and re-check key sensors after adjustments."
                        )
                    elif grow.stage in {"flowering", "ripening", "harvesting"}:
                        alert_type = f"coaching_stage_focus_{grow.id}"
                        title = "Flowering Stage Focus"
                        message = (
                            f"'{grow.name}' is in {grow.stage}. "
                            "Prioritize stable EC/pH trends and begin harvest-readiness checks this week."
                        )

                    if not (alert_type and title and message):
                        continue
                    if not _severity_allowed(severity, minimum_severity):
                        continue

                    existing = (
                        await session.execute(
                            select(AlertHistory).where(
                                AlertHistory.tenant_id == grow.tenant_id,
                                AlertHistory.grow_cycle_id == grow.id,
                                AlertHistory.alert_type == alert_type,
                                AlertHistory.created_at > cutoff,
                            )
                        )
                    ).scalar_one_or_none()
                    if existing:
                        continue

                    session.add(
                        AlertHistory(
                            tenant_id=grow.tenant_id,
                            grow_cycle_id=grow.id,
                            alert_type=alert_type,
                            severity=severity,
                            message=message,
                        )
                    )
                    await dispatch_alert(
                        session,
                        grow.tenant_id,
                        severity,
                        title,
                        message,
                        event_type="ai_coaching",
                    )
                    logger.info("Proactive coaching alert sent for grow %s (%s)", grow.id, alert_type)

                await session.commit()
        except Exception:
            logger.exception("Proactive coaching task failed")

    async def _integration_poll(self) -> None:
        """Poll integrations that are due for sync based on poll_interval_s."""
        from datetime import datetime

        from sqlalchemy import select

        from app.database import async_session_factory
        from app.integrations.connectors.base import get_connector_class
        from app.integrations.crypto import decrypt_config
        from app.integrations.models import IntegrationConfig, IntegrationDeviceMap

        try:
            async with async_session_factory() as session:
                now = datetime.now(UTC)
                result = await session.execute(
                    select(IntegrationConfig).where(
                        IntegrationConfig.enabled.is_(True),
                        IntegrationConfig.poll_interval_s.isnot(None),
                    )
                )
                configs = result.scalars().all()

                polled = 0
                for cfg in configs:
                    # Check if enough time has elapsed since last sync
                    if cfg.last_synced_at:
                        elapsed = (now - cfg.last_synced_at).total_seconds()
                        if cfg.poll_interval_s is not None and elapsed < cfg.poll_interval_s:
                            continue

                    connector_cls = get_connector_class(cfg.type)
                    if connector_cls is None:
                        continue

                    # Set RLS context for this tenant
                    from app.database import set_rls_tenant

                    await set_rls_tenant(session, cfg.tenant_id)

                    dm_result = await session.execute(
                        select(IntegrationDeviceMap).where(
                            IntegrationDeviceMap.integration_id == cfg.id,
                            IntegrationDeviceMap.enabled.is_(True),
                        )
                    )
                    device_maps = dm_result.scalars().all()

                    connector = connector_cls(
                        config=cfg,
                        decrypted_config=decrypt_config(cfg.config),
                        device_maps=list(device_maps),
                    )

                    try:
                        poll_result = await connector.poll()

                        # Persist readings to sensor tables
                        if poll_result.readings:
                            try:
                                written = await connector.persist_readings(session, poll_result)
                                logger.info(
                                    "Persisted %d readings for integration %s (%s)",
                                    written,
                                    cfg.id,
                                    cfg.type,
                                )
                            except Exception:
                                logger.exception(
                                    "Failed to persist readings for %s (%s)",
                                    cfg.id,
                                    cfg.type,
                                )
                                poll_result.errors.append("Reading persistence failed")

                        await connector.write_sync_log(session, poll_result)
                        cfg.last_synced_at = now
                        if poll_result.status == "error":
                            cfg.error_count += 1
                        else:
                            cfg.error_count = 0
                        polled += 1
                    except Exception:
                        logger.exception("Integration poll failed: %s (%s)", cfg.id, cfg.type)
                        cfg.error_count += 1

                if polled:
                    await session.commit()
                    logger.info("Polled %d integrations", polled)
                else:
                    logger.debug("Integration poll: none due")
        except Exception:
            logger.exception("Integration poll sweep failed")

    async def _dunning_check(self) -> None:
        """Check for expired grace periods and downgrade accounts to free."""
        from app.billing.dunning import check_expired_grace_periods

        try:
            await check_expired_grace_periods()
            logger.debug("Dunning check complete")
        except Exception:
            logger.exception("Dunning check failed")

    async def _account_purge(self) -> None:
        """Purge accounts whose deletion retention period has expired."""
        from app.billing.account_deletion import purge_expired_accounts

        try:
            await purge_expired_accounts()
            logger.debug("Account purge check complete")
        except Exception:
            logger.exception("Account purge check failed")

    async def _plan_reconcile(self) -> None:
        """Reconcile billing plans with payment providers (bidirectional sync)."""
        from app.billing.sync import reconcile_all_providers

        try:
            await reconcile_all_providers()
            logger.debug("Plan reconciliation complete")
        except Exception:
            logger.exception("Plan reconciliation failed")
