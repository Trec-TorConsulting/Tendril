"""AI API routes — chat (WebSocket), health check, coach tips, insights, reports."""
from __future__ import annotations

import json
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_token
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.ai.ollama import chat_completion, chat_completion_stream, vision_analysis
from app.ai.context import (
    build_chat_context,
    build_health_check_prompt,
    build_coach_tip_prompt,
    build_insight_prompt,
)

logger = logging.getLogger("tendril.ai")
router = APIRouter()


# ---------- WebSocket Chat (4.1) ----------

@router.websocket("/chat")
async def websocket_chat(ws: WebSocket):
    """AI chat via WebSocket. Expects token in first message for auth."""
    await ws.accept()

    # Auth: first message must be {"token": "...", "grow_id": "..."}
    try:
        init = await ws.receive_json()
        token = init.get("token", "")
        grow_id = init.get("grow_id")

        payload = decode_token(token)
        if payload.get("type") != "access":
            await ws.send_json({"error": "Invalid token"})
            await ws.close()
            return
        tenant_id = UUID(payload["tid"])
    except Exception:
        await ws.send_json({"error": "Authentication failed"})
        await ws.close()
        return

    # Load grow context
    system_context = "You are Tendril, an AI grow assistant."
    if grow_id:
        try:
            from app.database import async_session_factory
            from app.grows.models import GrowCycle, BucketSensorReading, Bucket, Tent, WeatherReading
            from sqlalchemy import text

            async with async_session_factory() as session:
                tid = str(tenant_id)
                await session.execute(text(f"SET app.current_tenant = '{tid}'"))
                grow = await session.get(GrowCycle, UUID(grow_id))
                if grow and grow.tenant_id == tenant_id:
                    # Get latest sensor data
                    buckets = (await session.execute(
                        select(Bucket).where(Bucket.grow_cycle_id == grow.id)
                    )).scalars().all()

                    recent_sensors = {}
                    if buckets:
                        reading = (await session.execute(
                            select(BucketSensorReading)
                            .where(BucketSensorReading.bucket_id == buckets[0].id)
                            .order_by(desc(BucketSensorReading.recorded_at))
                            .limit(1)
                        )).scalar_one_or_none()
                        if reading:
                            recent_sensors = {
                                "ph": reading.ph,
                                "ec": reading.ec,
                                "water_temp_f": reading.water_temp_f,
                                "ambient_temp_f": reading.ambient_temp_f,
                                "ambient_humidity": reading.ambient_humidity,
                            }

                    # Get weather if outdoor
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
                            weather = {
                                "temperature_c": w.temperature_c,
                                "humidity_pct": w.humidity_pct,
                                "wind_speed_kmh": w.wind_speed_kmh,
                                "uv_index": w.uv_index,
                            }

                    system_context = build_chat_context(
                        grow.grow_type,
                        stage=grow.stage,
                        recent_sensors=recent_sensors,
                        weather=weather,
                    )
        except Exception:
            logger.exception("Failed to load grow context for chat")

    messages = [{"role": "system", "content": system_context}]
    await ws.send_json({"type": "ready", "message": "Connected to Tendril AI"})

    # Chat loop
    try:
        while True:
            data = await ws.receive_json()
            user_msg = data.get("message", "")
            if not user_msg:
                continue

            messages.append({"role": "user", "content": user_msg})

            # Stream response
            full_response = ""
            try:
                async for chunk in chat_completion_stream(messages):
                    full_response += chunk
                    await ws.send_json({"type": "chunk", "content": chunk})
            except Exception:
                logger.exception("Ollama stream error")
                await ws.send_json({"type": "error", "message": "AI service unavailable"})
                continue

            messages.append({"role": "assistant", "content": full_response})
            await ws.send_json({"type": "done", "content": full_response})

    except WebSocketDisconnect:
        logger.debug("Chat WebSocket disconnected")


# ---------- Health Check (4.2) ----------

class HealthCheckRequest(BaseModel):
    grow_id: str
    observations: dict[str, str]
    image_url: str | None = None


class HealthCheckResponse(BaseModel):
    score: int | None = None
    issues: list[str] = []
    actions: list[str] = []
    raw_analysis: str = ""


@router.post("/health-check", response_model=HealthCheckResponse)
async def run_health_check(
    body: HealthCheckRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Run an AI health check on a grow cycle."""
    from app.grows.models import GrowCycle, BucketSensorReading, Bucket, Tent, WeatherReading

    grow = await session.get(GrowCycle, UUID(body.grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

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
            sensors = {
                "ph": reading.ph,
                "ec": reading.ec,
                "water_temp_f": reading.water_temp_f,
                "ambient_temp_f": reading.ambient_temp_f,
                "ambient_humidity": reading.ambient_humidity,
            }

    # Gather weather for outdoor
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
            weather = {
                "temperature_c": w.temperature_c,
                "humidity_pct": w.humidity_pct,
                "precipitation_mm": w.precipitation_mm,
                "wind_speed_kmh": w.wind_speed_kmh,
                "uv_index": w.uv_index,
            }

    # Vision analysis if image provided
    vision_text = ""
    if body.image_url:
        try:
            vision_text = await vision_analysis(
                body.image_url,
                f"Analyze this {grow.grow_type} plant in {grow.stage} stage. "
                "Describe plant health, leaf color, root condition if visible, and any signs of disease or deficiency.",
            )
        except Exception:
            logger.exception("Vision analysis failed")

    if vision_text:
        body.observations["ai_vision"] = vision_text

    messages = build_health_check_prompt(
        grow.grow_type, grow.stage, body.observations, sensors, weather
    )

    try:
        raw = await chat_completion(messages)
    except Exception:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    # Parse JSON response
    try:
        parsed = json.loads(raw)
        return HealthCheckResponse(
            score=parsed.get("score"),
            issues=parsed.get("issues", []),
            actions=parsed.get("actions", []),
            raw_analysis=raw,
        )
    except json.JSONDecodeError:
        return HealthCheckResponse(raw_analysis=raw)


# ---------- Coach Tips (4.3) ----------

class CoachTipRequest(BaseModel):
    grow_id: str


class CoachTipResponse(BaseModel):
    tip: str


@router.post("/coach-tip", response_model=CoachTipResponse)
async def get_coach_tip(
    body: CoachTipRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get an AI coach tip for a specific grow cycle."""
    from app.grows.models import GrowCycle, BucketSensorReading, Bucket

    grow = await session.get(GrowCycle, UUID(body.grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

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

    messages = build_coach_tip_prompt(grow.grow_type, grow.stage, sensors)

    try:
        tip = await chat_completion(messages)
    except Exception:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    return CoachTipResponse(tip=tip.strip())


# ---------- AI Insights (4.13) ----------

class InsightRequest(BaseModel):
    grow_id: str
    insight_type: str  # harvest_predict | nutrient_advice | anomaly_scan


class InsightResponse(BaseModel):
    insight_type: str
    result: dict | str


@router.post("/insights", response_model=InsightResponse)
async def get_insight(
    body: InsightRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get AI-powered insights for a grow cycle."""
    from app.grows.models import GrowCycle, BucketSensorReading, Bucket

    if body.insight_type not in ("harvest_predict", "nutrient_advice", "anomaly_scan"):
        raise HTTPException(status_code=400, detail="Invalid insight type")

    grow = await session.get(GrowCycle, UUID(body.grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    data = {
        "grow_type": grow.grow_type,
        "stage": grow.stage,
        "status": grow.status,
        "started_at": str(grow.started_at),
    }

    # Add sensor summary
    buckets = (await session.execute(
        select(Bucket).where(Bucket.grow_cycle_id == grow.id)
    )).scalars().all()
    if buckets:
        readings = (await session.execute(
            select(BucketSensorReading)
            .where(BucketSensorReading.bucket_id == buckets[0].id)
            .order_by(desc(BucketSensorReading.recorded_at))
            .limit(10)
        )).scalars().all()
        if readings:
            ph_vals = [r.ph for r in readings if r.ph is not None]
            ec_vals = [r.ec for r in readings if r.ec is not None]
            if ph_vals:
                data["ph_avg"] = round(sum(ph_vals) / len(ph_vals), 2)
                data["ph_range"] = f"{min(ph_vals)}-{max(ph_vals)}"
            if ec_vals:
                data["ec_avg"] = round(sum(ec_vals) / len(ec_vals), 2)
                data["ec_range"] = f"{min(ec_vals)}-{max(ec_vals)}"
            data["reading_count"] = len(readings)

    messages = build_insight_prompt(body.insight_type, grow.grow_type, data)

    try:
        raw = await chat_completion(messages)
    except Exception:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = raw

    return InsightResponse(insight_type=body.insight_type, result=result)


# ---------- PDF Report (4.14) ----------

@router.get("/report/{grow_id}")
async def get_grow_report(
    grow_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Generate a PDF report for a grow cycle."""
    from fastapi.responses import Response
    from app.ai.reports import generate_grow_report

    try:
        pdf_bytes = await generate_grow_report(session, UUID(grow_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="grow-report-{grow_id[:8]}.pdf"'},
    )
