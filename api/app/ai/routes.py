"""AI API routes — chat (WebSocket), health check, coach tips, insights, reports."""
from __future__ import annotations

import base64
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
from app.ai.ollama import chat_completion, chat_completion_stream, chat_with_tools
from app.ai.context import (
    build_chat_context,
    build_health_check_prompt,
    build_coach_tip_prompt,
    build_insight_prompt,
    build_feeding_advice_prompt,
)
from app.ai.gather import gather_grow_data
from app.ai.tools import CHAT_TOOLS, execute_tool

logger = logging.getLogger("tendril.ai")
router = APIRouter()

MAX_TOOL_ROUNDS = 5


# ---------- WebSocket Chat (4.1) — with tool support ----------

@router.websocket("/chat")
async def websocket_chat(ws: WebSocket):
    """AI chat via WebSocket with full grow context and tool-calling support."""
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

    # Load full grow context
    system_context = "You are Tendril, an AI grow assistant."
    grow_uuid = None
    if grow_id:
        try:
            from app.database import async_session_factory
            from app.grows.models import GrowCycle
            from sqlalchemy import text

            async with async_session_factory() as session:
                tid = str(tenant_id)
                await session.execute(text(f"SET app.current_tenant = '{tid}'"))
                grow = await session.get(GrowCycle, UUID(grow_id))
                if grow and grow.tenant_id == tenant_id:
                    grow_uuid = grow.id
                    grow_data = await gather_grow_data(session, grow, include_camera=False)
                    system_context = build_chat_context(grow_data)
        except Exception:
            logger.exception("Failed to load grow context for chat")

    messages = [{"role": "system", "content": system_context}]
    await ws.send_json({"type": "ready", "message": "Connected to Tendril AI"})

    # Chat loop with tool support
    try:
        while True:
            data = await ws.receive_json()
            user_msg = data.get("message", "")
            if not user_msg:
                continue

            messages.append({"role": "user", "content": user_msg})

            # Tool-calling loop: detect tool calls, execute, re-query
            tool_used = False
            if grow_uuid:
                for _round in range(MAX_TOOL_ROUNDS):
                    try:
                        result = await chat_with_tools(messages, CHAT_TOOLS)
                    except Exception:
                        logger.exception("Ollama tool call failed")
                        break

                    tool_calls = result.get("tool_calls")
                    if not tool_calls:
                        break

                    # Model wants to call tools
                    tool_used = True
                    messages.append(result["message"])

                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        fn_name = fn.get("name", "")
                        fn_args = fn.get("arguments", {})

                        try:
                            from app.database import async_session_factory
                            from sqlalchemy import text

                            async with async_session_factory() as tool_session:
                                tid = str(tenant_id)
                                await tool_session.execute(
                                    text(f"SET app.current_tenant = '{tid}'")
                                )
                                tool_result = await execute_tool(
                                    fn_name, fn_args,
                                    session=tool_session,
                                    tenant_id=tenant_id,
                                    grow_id=grow_uuid,
                                )
                        except Exception as e:
                            logger.exception("Tool execution error")
                            tool_result = f"Error: {e}"

                        messages.append({"role": "tool", "content": tool_result})
                        await ws.send_json({
                            "type": "action",
                            "tool": fn_name,
                            "result": tool_result,
                        })

            # Stream the final natural-language response
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


# ---------- Health Check (4.2) — powered by Gemini with camera + full data ----------

class HealthCheckRequest(BaseModel):
    grow_id: str
    observations: dict[str, str]
    image_base64: str | None = None
    include_camera: bool = True


class HealthCheckResponse(BaseModel):
    id: str | None = None
    score: int | None = None
    issues: list[str] = []
    actions: list[str] = []
    raw_analysis: str = ""
    source: str = "manual"
    created_at: str | None = None


class HealthCheckHistoryResponse(BaseModel):
    items: list[HealthCheckResponse]


@router.post("/health-check", response_model=HealthCheckResponse)
async def run_health_check(
    body: HealthCheckRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Run a Gemini-powered AI health check with camera image and full grow data."""
    from app.grows.models import GrowCycle, HealthEval
    from app.ai.gemini import (
        chat_completion as gemini_chat,
        is_configured as gemini_configured,
        GeminiRateLimitError,
    )

    if not gemini_configured():
        raise HTTPException(status_code=503, detail="AI health check service not configured")

    grow = await session.get(GrowCycle, UUID(body.grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    # Gather ALL data
    grow_data = await gather_grow_data(
        session, grow, include_camera=body.include_camera,
    )

    # Build prompt with all data
    messages = build_health_check_prompt(grow_data, body.observations)

    # Prepare images for Gemini
    camera_image: bytes | None = grow_data.get("camera_image")
    extra_images: list[tuple[str, bytes]] = []
    if body.image_base64:
        try:
            user_image = base64.b64decode(body.image_base64)
            if camera_image:
                extra_images.append(("User uploaded photo", user_image))
            else:
                camera_image = user_image
        except Exception:
            logger.warning("Invalid base64 image from user")

    try:
        raw = await gemini_chat(
            messages,
            image_bytes=camera_image,
            extra_images=extra_images or None,
        )
    except GeminiRateLimitError:
        raise HTTPException(
            status_code=429,
            detail="AI rate limit reached. Try again in a few minutes.",
        )
    except Exception:
        logger.exception("Gemini health check failed")
        raise HTTPException(status_code=503, detail="AI service unavailable")

    # Parse JSON response
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
        logger.warning("Gemini returned non-JSON: %s", raw[:200])

    # Store the eval
    health_eval = HealthEval(
        tenant_id=grow.tenant_id,
        grow_cycle_id=grow.id,
        score=score,
        issues=issues,
        actions=actions,
        raw_analysis=raw,
        source="manual",
    )
    session.add(health_eval)

    # Invalidate cached feeding advice so next request regenerates
    grow.cached_feeding_advice = None
    grow.feeding_advice_cached_at = None

    # Save camera snapshot as a grow photo for the gallery
    if camera_image and not body.image_base64:
        # Only auto-save the camera image (not user-uploaded duplicates)
        try:
            import asyncio
            from app.grows.models import GrowPhoto
            from app.storage import upload_photo as s3_upload

            loop = asyncio.get_running_loop()
            key = await loop.run_in_executor(
                None, s3_upload, camera_image, "image/jpeg",
                str(grow.tenant_id), str(grow.id),
            )
            grow_photo = GrowPhoto(
                tenant_id=grow.tenant_id,
                grow_cycle_id=grow.id,
                source="health_check",
                storage_key=key,
                caption=f"Health check snapshot (score: {score})" if score else "Health check snapshot",
            )
            session.add(grow_photo)
        except Exception:
            logger.warning("Failed to save health check snapshot to S3")

    await session.commit()
    await session.refresh(health_eval)

    return HealthCheckResponse(
        id=str(health_eval.id),
        score=score,
        issues=issues,
        actions=actions,
        raw_analysis=raw,
        source="manual",
        created_at=health_eval.created_at.isoformat(),
    )


@router.get("/health-check/{grow_id}/history", response_model=HealthCheckHistoryResponse)
async def get_health_check_history(
    grow_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    limit: int = 10,
):
    """Get health check history for a grow cycle."""
    from app.grows.models import HealthEval

    evals = (await session.execute(
        select(HealthEval)
        .where(HealthEval.grow_cycle_id == UUID(grow_id))
        .order_by(desc(HealthEval.created_at))
        .limit(min(limit, 50))
    )).scalars().all()

    return HealthCheckHistoryResponse(
        items=[
            HealthCheckResponse(
                id=str(e.id),
                score=e.score,
                issues=e.issues or [],
                actions=e.actions or [],
                raw_analysis=e.raw_analysis,
                source=e.source,
                created_at=e.created_at.isoformat(),
            )
            for e in evals
        ]
    )


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


# ---------- Feeding Advice (AI-powered) ----------

class FeedingAdviceResponse(BaseModel):
    current_stage_advice: str | None = None
    adjustments: list[dict] = []
    alerts: list[dict] = []
    next_transition: dict | None = None
    health_impact: str | None = None


@router.get("/feeding-advice/{grow_id}", response_model=FeedingAdviceResponse)
async def get_feeding_advice(
    grow_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """AI-powered feeding recommendations — cached until the next health check."""
    from datetime import datetime, timezone
    from app.grows.models import GrowCycle, HealthEval

    grow = await session.get(GrowCycle, UUID(grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    # Check if we have a valid cache: advice exists and no newer health eval
    if grow.cached_feeding_advice and grow.feeding_advice_cached_at:
        latest_eval = (await session.execute(
            select(HealthEval)
            .where(HealthEval.grow_cycle_id == grow.id)
            .order_by(desc(HealthEval.created_at))
            .limit(1)
        )).scalar_one_or_none()

        cache_valid = True
        if latest_eval and latest_eval.created_at > grow.feeding_advice_cached_at:
            cache_valid = False  # New health check since last cache

        if cache_valid:
            cached = grow.cached_feeding_advice
            return FeedingAdviceResponse(
                current_stage_advice=cached.get("current_stage_advice"),
                adjustments=cached.get("adjustments") or [],
                alerts=cached.get("alerts") or [],
                next_transition=cached.get("next_transition"),
                health_impact=cached.get("health_impact"),
            )

    # Cache miss or stale — regenerate
    grow_data = await gather_grow_data(session, grow, include_camera=False)
    messages = build_feeding_advice_prompt(grow_data)

    try:
        raw = await chat_completion(messages)
    except Exception:
        logger.exception("Feeding advice AI call failed")
        # If we have stale cache, return it rather than erroring
        if grow.cached_feeding_advice:
            cached = grow.cached_feeding_advice
            return FeedingAdviceResponse(
                current_stage_advice=cached.get("current_stage_advice"),
                adjustments=cached.get("adjustments") or [],
                alerts=cached.get("alerts") or [],
                next_transition=cached.get("next_transition"),
                health_impact=cached.get("health_impact"),
            )
        raise HTTPException(status_code=503, detail="AI service unavailable")

    # Parse JSON response
    try:
        cleaned = raw.strip()
        if "```" in cleaned:
            parts = cleaned.split("```")
            for part in parts[1:]:
                candidate = part.strip()
                if candidate.lower().startswith("json"):
                    candidate = candidate[4:].strip()
                if candidate.startswith("{"):
                    cleaned = candidate
                    break
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
        if not cleaned.startswith("{"):
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start:end + 1]
        parsed = json.loads(cleaned)

        # Cache the parsed result on the grow
        grow.cached_feeding_advice = parsed
        grow.feeding_advice_cached_at = datetime.now(timezone.utc)
        await session.commit()

        return FeedingAdviceResponse(
            current_stage_advice=parsed.get("current_stage_advice"),
            adjustments=parsed.get("adjustments") or [],
            alerts=parsed.get("alerts") or [],
            next_transition=parsed.get("next_transition"),
            health_impact=parsed.get("health_impact"),
        )
    except (json.JSONDecodeError, Exception):
        logger.warning("Could not parse feeding advice JSON, returning raw")
        return FeedingAdviceResponse(current_stage_advice=raw[:500])


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
