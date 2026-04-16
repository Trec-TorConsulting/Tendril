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
        """Run AI health checks for active grows via Ollama."""
        from app.database import async_session_factory
        from app.grows.models import GrowCycle, Bucket, BucketSensorReading, Tent, WeatherReading
        from app.ai.ollama import chat_completion
        from app.ai.context import build_health_check_prompt
        from sqlalchemy import select, desc

        try:
            async with async_session_factory() as session:
                grows = (await session.execute(
                    select(GrowCycle).where(GrowCycle.status == "active")
                )).scalars().all()

                for grow in grows:
                    try:
                        # Gather sensor data
                        sensors = {}
                        buckets = (await session.execute(
                            select(Bucket).where(Bucket.grow_cycle_id == grow.id)
                        )).scalars().all()
                        if buckets:
                            reading = (await session.execute(
                                select(BucketSensorReading)
                                .where(BucketSensorReading.bucket_id == buckets[0].id)
                                .order_by(desc(BucketSensorReading.recorded_at))
                                .limit(1)
                            )).scalar_one_or_none()
                            if reading:
                                sensors = {"ph": reading.ph, "ec": reading.ec, "water_temp_f": reading.water_temp_f}

                        # Get weather for outdoor tents
                        weather = None
                        tent = await session.get(Tent, grow.tent_id)
                        if tent and tent.environment_type in ("outdoor", "greenhouse"):
                            w = (await session.execute(
                                select(WeatherReading)
                                .where(WeatherReading.tent_id == tent.id)
                                .order_by(desc(WeatherReading.recorded_at))
                                .limit(1)
                            )).scalar_one_or_none()
                            if w:
                                weather = {"temperature_c": w.temperature_c, "humidity_pct": w.humidity_pct}

                        observations = {"automated_check": "Scheduled health check"}
                        messages = build_health_check_prompt(
                            grow.grow_type, grow.stage, observations, sensors, weather
                        )
                        result = await chat_completion(messages)
                        logger.info("Health check for grow %s: %s", grow.id, result[:100])
                    except Exception:
                        logger.exception("Health check failed for grow %s", grow.id)

                logger.info("Health checks completed for %d active grows", len(grows))
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
