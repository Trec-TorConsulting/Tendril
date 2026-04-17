"""Scheduler task definitions."""
from __future__ import annotations

import asyncio
import logging

from app.config import Settings

logger = logging.getLogger("tendril.scheduler.tasks")

# Task intervals in seconds
HEALTH_CHECK_INTERVAL = 12 * 3600    # 12 hours
WEATHER_POLL_INTERVAL = 30 * 60      # 30 minutes
ALERT_EVAL_INTERVAL = 60             # 1 minute
RULE_EVAL_INTERVAL = 30              # 30 seconds
RETENTION_INTERVAL = 24 * 3600       # Daily
DAILY_REPORT_INTERVAL = 24 * 3600    # Daily


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
            except asyncio.TimeoutError:
                pass

    async def _health_check(self) -> None:
        """Run Gemini health checks for active grows with auto_health_check enabled.

        Uses full grow data (sensors, trends, feeding, journal, camera) for maximum detail.
        """
        from app.database import async_session_factory
        from app.grows.models import GrowCycle, HealthEval
        from app.ai.gemini import chat_completion as gemini_chat, is_configured as gemini_configured, GeminiRateLimitError
        from app.ai.context import build_health_check_prompt
        from app.ai.gather import gather_grow_data
        from sqlalchemy import select, desc

        if not gemini_configured():
            logger.warning("Gemini API key not configured — skipping scheduled health checks")
            return

        try:
            async with async_session_factory() as session:
                grows = (await session.execute(
                    select(GrowCycle).where(
                        GrowCycle.status == "active",
                        GrowCycle.auto_health_check.is_(True),
                    )
                )).scalars().all()

                if not grows:
                    logger.debug("No active grows with auto_health_check enabled")
                    return

                for grow in grows:
                    try:
                        # Check if last eval is recent enough (skip if < 11h to avoid drift)
                        prev = (await session.execute(
                            select(HealthEval)
                            .where(HealthEval.grow_cycle_id == grow.id)
                            .order_by(desc(HealthEval.created_at))
                            .limit(1)
                        )).scalar_one_or_none()

                        if prev:
                            from datetime import datetime, timezone
                            age_hours = (datetime.now(timezone.utc) - prev.created_at).total_seconds() / 3600
                            if age_hours < 11:
                                logger.debug("Grow %s last eval %.1fh ago — skipping", grow.id, age_hours)
                                continue

                        # Gather ALL data including camera snapshot
                        grow_data = await gather_grow_data(
                            session, grow, include_camera=True,
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
                        await session.commit()

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
        from app.database import async_session_factory
        from app.grows.models import Tent, WeatherReading
        from app.weather.client import fetch_weather
        from sqlalchemy import select

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
        from app.database import async_session_factory
        from app.grows.models import Tent, WeatherReading
        from app.automation.models import AlertHistory
        from app.automation.engine import WEATHER_RULES, OPERATORS
        from sqlalchemy import select, desc
        from datetime import timedelta

        try:
            async with async_session_factory() as session:
                tents = (await session.execute(
                    select(Tent).where(
                        Tent.environment_type.in_(["outdoor", "greenhouse"]),
                    )
                )).scalars().all()

                for tent in tents:
                    w = (await session.execute(
                        select(WeatherReading)
                        .where(WeatherReading.tent_id == tent.id)
                        .order_by(desc(WeatherReading.recorded_at))
                        .limit(1)
                    )).scalar_one_or_none()
                    if not w:
                        continue

                    for rule in WEATHER_RULES:
                        value = getattr(w, rule["sensor"], None)
                        if value is None:
                            continue
                        op_fn = OPERATORS.get(rule["condition"])
                        if op_fn and op_fn(value, rule["threshold"]):
                            # Check if alert already fired recently (1h cooldown)
                            from datetime import datetime, timezone
                            cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
                            existing = (await session.execute(
                                select(AlertHistory)
                                .where(
                                    AlertHistory.tenant_id == tent.tenant_id,
                                    AlertHistory.alert_type == f"weather_{rule['type']}",
                                    AlertHistory.created_at > cutoff,
                                )
                            )).scalar_one_or_none()
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

                            # Dispatch notification
                            from app.notifications.service import dispatch_alert
                            await dispatch_alert(
                                session, tent.tenant_id, rule["severity"],
                                f"Weather Alert: {rule['type']}",
                                rule["message"],
                            )

                await session.commit()
        except Exception:
            logger.exception("Alert eval task failed")

    async def _rule_eval(self) -> None:
        """Evaluate automation rules against latest sensor readings."""
        from app.database import async_session_factory
        from app.automation.engine import evaluate_rules

        try:
            async with async_session_factory() as session:
                triggered = await evaluate_rules(session)
                if triggered:
                    logger.info("Rule eval triggered %d alerts", len(triggered))
        except Exception:
            logger.exception("Rule eval task failed")

    async def _daily_report(self) -> None:
        """Generate daily grow reports and dispatch notifications."""
        from app.database import async_session_factory
        from app.grows.models import GrowCycle
        from app.ai.reports import generate_grow_report
        from app.notifications.service import dispatch_alert
        from sqlalchemy import select

        try:
            async with async_session_factory() as session:
                grows = (await session.execute(
                    select(GrowCycle).where(GrowCycle.status == "active")
                )).scalars().all()

                for grow in grows:
                    try:
                        await generate_grow_report(session, grow.id)
                        logger.info("Daily report generated for grow %s", grow.id)
                    except Exception:
                        logger.exception("Daily report failed for grow %s", grow.id)

                # Send daily digest notification per tenant
                tenant_ids = set(g.tenant_id for g in grows)
                for tid in tenant_ids:
                    grow_count = sum(1 for g in grows if g.tenant_id == tid)
                    await dispatch_alert(
                        session, tid, "info",
                        "Daily Grow Report",
                        f"Daily health reports generated for {grow_count} active grow(s).",
                    )

                logger.info("Daily reports completed for %d grows", len(grows))
        except Exception:
            logger.exception("Daily report task failed")

    async def _data_retention(self) -> None:
        """Prune old sensor data per tenant retention settings."""
        from app.database import async_session_factory
        from app.data.service import enforce_retention

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
