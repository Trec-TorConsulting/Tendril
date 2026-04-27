"""Scheduler task definitions."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC

from app.config import Settings

logger = logging.getLogger("tendril.scheduler.tasks")

# Task intervals in seconds
HEALTH_CHECK_INTERVAL = 12 * 3600  # 12 hours
WEATHER_POLL_INTERVAL = 30 * 60  # 30 minutes
ALERT_EVAL_INTERVAL = 60  # 1 minute
RULE_EVAL_INTERVAL = 30  # 30 seconds
RETENTION_INTERVAL = 24 * 3600  # Daily
DAILY_REPORT_INTERVAL = 24 * 3600  # Daily
HARVEST_CHECK_INTERVAL = 4 * 3600  # 4 hours
TASK_GENERATION_INTERVAL = 6 * 3600  # 6 hours
INTEGRATION_POLL_INTERVAL = 60  # 1 minute (checks due integrations)


class TaskRunner:
    def __init__(self, settings: Settings):
        self.settings = settings

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
                self._loop(shutdown_event, "integration_poll", INTEGRATION_POLL_INTERVAL, self._integration_poll)
            ),
        ]
        await shutdown_event.wait()
        for t in tasks:
            t.cancel()

    async def _loop(
        self,
        shutdown_event: asyncio.Event,
        name: str,
        interval: float,
        func,
    ) -> None:
        while not shutdown_event.is_set():
            try:
                await func()
            except Exception:
                logger.exception("Error in task %s", name)
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=interval)
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
                        messages = build_health_check_prompt(grow_data, observations)

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
                            issues = parsed.get("issues", [])
                            actions = parsed.get("actions", [])
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
                                logger.warning("Failed to save scheduled snapshot to S3 for grow %s", grow.id)

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
                        value = getattr(w, rule["sensor"], None)
                        if value is None:
                            continue
                        op_fn = OPERATORS.get(rule["condition"])
                        if op_fn and op_fn(value, rule["threshold"]):
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
                                    severity=rule["severity"],
                                    alert_type=f"weather_{rule['type']}",
                                    message=rule["message"],
                                    sensor_value=value,
                                )
                            except Exception:
                                logger.exception("Failed to create task from weather alert")

                            # Dispatch notification
                            from app.notifications.service import dispatch_alert

                            await dispatch_alert(
                                session,
                                tent.tenant_id,
                                rule["severity"],
                                f"Weather Alert: {rule['type']}",
                                rule["message"],
                            )

                await session.commit()
        except Exception:
            logger.exception("Alert eval task failed")

    async def _rule_eval(self) -> None:
        """Evaluate automation rules against latest sensor readings."""
        from app.automation.engine import evaluate_rules
        from app.database import async_session_factory

        try:
            async with async_session_factory() as session:
                triggered = await evaluate_rules(session)
                if triggered:
                    logger.info("Rule eval triggered %d alerts", len(triggered))
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
                        if elapsed < cfg.poll_interval_s:
                            continue

                    connector_cls = get_connector_class(cfg.type)
                    if connector_cls is None:
                        continue

                    # Set RLS context for this tenant
                    from sqlalchemy import text

                    await session.execute(
                        text("SET app.current_tenant = :tid"),
                        {"tid": str(cfg.tenant_id)},
                    )

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
