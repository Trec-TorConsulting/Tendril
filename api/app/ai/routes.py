"""AI API routes — chat (WebSocket), health check, coach tips, insights, reports."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from contextlib import suppress
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import service
from app.ai.context import (
    build_chat_context,
    build_coach_tip_prompt,
    build_feeding_advice_prompt,
    build_health_check_prompt,
    build_insight_prompt,
)
from app.ai.gather import gather_grow_data
from app.ai.integration_policy import IntegrationActionPolicyDecision, evaluate_integration_action_policy
from app.ai.ollama import chat_completion, chat_completion_stream, chat_with_tools
from app.ai.tools import CHAT_TOOLS, execute_tool
from app.auth.jwt import decode_token
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.billing.metering import record_usage
from app.billing.tier_gate import require_usage_limit

logger = logging.getLogger("tendril.ai")
router = APIRouter()

MAX_TOOL_ROUNDS = 5
KEEPALIVE_INTERVAL_SECONDS = 20


def _build_keepalive_event() -> dict[str, str]:
    """Build the websocket keepalive payload sent during long AI work."""
    return {
        "type": "ping",
        "ts": datetime.now(UTC).isoformat(),
    }


def _build_chat_action_event(
    *,
    phase: str,
    tool: str,
    message: str,
    action_id: str | None = None,
    correlation_id: str | None = None,
    result: Any | None = None,
    error: str | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a structured chat action lifecycle event for websocket clients."""
    payload: dict[str, Any] = {
        "type": "action_event",
        "phase": phase,
        "tool": tool,
        "message": message,
        "refresh_actions": True,
        "ts": datetime.now(UTC).isoformat(),
    }
    if action_id is not None:
        payload["action_id"] = action_id
    if correlation_id is not None:
        payload["correlation_id"] = correlation_id
    if result is not None:
        payload["result"] = result
    if error is not None:
        payload["error"] = error
    if policy is not None:
        payload["policy"] = policy
    return payload


def _extract_integration_type_from_tool_arguments(tool_arguments: Any) -> str | None:
    """Extract connector type from tool arguments for policy evaluation."""
    if not isinstance(tool_arguments, dict):
        return None

    for key in ("integration_type", "connector_type", "connector"):
        value = tool_arguments.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _resolve_integration_policy_for_tool_call(
    *,
    tool_name: str,
    tool_arguments: Any,
) -> IntegrationActionPolicyDecision | None:
    """Resolve policy decision for integration-prefixed tool calls."""
    if not tool_name.startswith("integration_"):
        return None

    integration_type = _extract_integration_type_from_tool_arguments(tool_arguments)
    if integration_type is None:
        return None

    operation = tool_name.removeprefix("integration_")
    return evaluate_integration_action_policy(
        integration_type=integration_type,
        operation=operation,
    )


def _build_policy_payload(decision: IntegrationActionPolicyDecision) -> dict[str, Any]:
    """Serialize a policy decision for websocket lifecycle events."""
    return {
        "integration_type": decision.integration_type,
        "operation": decision.operation,
        "supported": decision.supported,
        "allowed": decision.allowed,
        "risk_level": decision.risk_level,
        "requires_approval": decision.requires_approval,
        "requires_simulation": decision.requires_simulation,
        "reason": decision.reason,
    }


def _extract_action_id_from_tool_result(tool_result: Any) -> str | None:
    """Extract a persisted agent action ID from tool output when available."""
    if not isinstance(tool_result, dict):
        return None

    for key in ("action_id", "agent_action_id"):
        value = tool_result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_action_id_from_tool_arguments(tool_arguments: Any) -> str | None:
    """Extract a persisted agent action ID from tool arguments when available."""
    if not isinstance(tool_arguments, dict):
        return None

    for key in ("action_id", "agent_action_id"):
        value = tool_arguments.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _resolve_action_event_ids(
    *,
    tool_call_id: str | None,
    tool_arguments: Any,
    tool_result: Any | None = None,
) -> tuple[str | None, str | None]:
    """Resolve normalized action_id and correlation_id for websocket lifecycle events."""
    correlation_id = tool_call_id.strip() if isinstance(tool_call_id, str) and tool_call_id.strip() else None
    action_from_args = _extract_action_id_from_tool_arguments(tool_arguments)
    action_from_result = _extract_action_id_from_tool_result(tool_result) if tool_result is not None else None
    action_id = action_from_result or action_from_args or correlation_id
    return action_id, correlation_id


async def _send_keepalive_pings(ws: WebSocket, stop_event: asyncio.Event) -> None:
    """Send periodic keepalive pings while the websocket is open."""
    while not stop_event.is_set():
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=KEEPALIVE_INTERVAL_SECONDS)
            break
        except TimeoutError:
            try:
                await ws.send_json(_build_keepalive_event())
            except Exception:
                break


# ---------- WebSocket Chat (4.1) — with tool support ----------


@router.websocket("/chat")
async def websocket_chat(ws: WebSocket):
    """AI chat via WebSocket with full grow context and tool-calling support."""
    await ws.accept()

    # Auth: first message must be {"token": "...", "grow_id": "..."}
    # Token may also come from httpOnly cookie on the WS handshake.
    try:
        init = await ws.receive_json()
        token = init.get("token", "")
        grow_id = init.get("grow_id")

        # Prefer cookie-based auth (httpOnly cookie sent with WS upgrade)
        cookie_token = ws.cookies.get("access_token")
        if cookie_token:
            token = cookie_token

        payload = decode_token(token)
        if payload.get("type") != "access":
            await ws.send_json({"type": "error", "message": "Authentication failed: invalid token"})
            await ws.close()
            return
        tenant_id = UUID(payload["tid"])
    except Exception:
        await ws.send_json({"type": "error", "message": "Authentication failed"})
        await ws.close()
        return

    keepalive_stop = asyncio.Event()
    keepalive_task = asyncio.create_task(_send_keepalive_pings(ws, keepalive_stop))

    # Load full grow context
    system_context = "You are Tendril, an AI grow assistant."
    grow_uuid = None
    if grow_id:
        try:
            from app.database import async_session_factory, set_rls_tenant
            from app.grows.models import GrowCycle

            async with async_session_factory() as session:
                await set_rls_tenant(session, tenant_id)
                grow = await session.get(GrowCycle, UUID(grow_id))
                if grow and grow.tenant_id == tenant_id:
                    grow_uuid = grow.id
                    grow_data = await asyncio.wait_for(
                        gather_grow_data(session, grow, include_camera=False),
                        timeout=10.0,
                    )
                    system_context = await build_chat_context(grow_data, session=session)
                    logger.info(
                        "Chat context loaded for grow %s (%s/%s), context length: %d chars",
                        grow.name,
                        grow.grow_type,
                        grow.stage,
                        len(system_context),
                    )
                else:
                    logger.warning("Chat: grow_id %s not found or tenant mismatch", grow_id)
        except TimeoutError:
            logger.warning("Timed out loading grow context for chat, using default")
        except Exception:
            logger.exception("Failed to load grow context for chat")
    else:
        logger.info("Chat: no grow_id provided, using generic context")

    messages: list[dict[str, Any]] = [{"role": "system", "content": system_context}]
    await ws.send_json({"type": "ready", "message": "Connected to Tendril AI"})

    # Conversation persistence: create or load conversation
    conversation_id = init.get("conversation_id")
    conv_uuid = None
    try:
        from app.ai.models import Conversation, ConversationMessage
        from app.database import async_session_factory, set_rls_tenant

        if conversation_id:
            conv_uuid = UUID(conversation_id)
            # Load existing messages
            async with async_session_factory() as session:
                await set_rls_tenant(session, tenant_id)
                from sqlalchemy.orm import selectinload

                result = await session.execute(
                    select(Conversation)
                    .options(selectinload(Conversation.messages))
                    .where(Conversation.id == conv_uuid, Conversation.tenant_id == tenant_id)
                )
                conv = result.scalar_one_or_none()
                if conv:
                    for msg in conv.messages:
                        if msg.role != "system":
                            messages.append({"role": msg.role, "content": msg.content})
        else:
            # Create new conversation
            async with async_session_factory() as session:
                await set_rls_tenant(session, tenant_id)
                conv = Conversation(
                    tenant_id=tenant_id,
                    user_id=UUID(payload["sub"]),
                    grow_cycle_id=grow_uuid,
                )
                session.add(conv)
                await session.commit()
                await session.refresh(conv)
                conv_uuid = conv.id
                await ws.send_json({"type": "conversation_id", "id": str(conv_uuid)})
    except Exception:
        logger.warning("Failed to load/create conversation, continuing without persistence")

    # Chat loop with tool support
    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "pong":
                continue

            user_msg = data.get("message", "")
            if not user_msg:
                continue

            messages.append({"role": "user", "content": user_msg})

            # Persist user message
            if conv_uuid:
                try:
                    async with async_session_factory() as session:
                        await set_rls_tenant(session, tenant_id)
                        session.add(ConversationMessage(conversation_id=conv_uuid, role="user", content=user_msg))
                        conv = await session.get(Conversation, conv_uuid)
                        if conv:
                            conv.message_count = (conv.message_count or 0) + 1
                        await session.commit()
                except Exception:
                    logger.debug("Failed to persist user message")

            # Tool-calling loop: detect tool calls, execute, re-query
            if grow_uuid:
                for _round in range(MAX_TOOL_ROUNDS):
                    try:
                        tool_result = await chat_with_tools(messages, CHAT_TOOLS)
                    except Exception:
                        logger.exception("Ollama tool call failed")
                        break

                    tool_calls = tool_result.get("tool_calls")
                    if not tool_calls:
                        break

                    # Model wants to call tools
                    messages.append(tool_result["message"])

                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        fn_name = fn.get("name", "")
                        fn_args = fn.get("arguments", {})
                        tool_call_id = tc.get("id") if isinstance(tc.get("id"), str) else None
                        event_action_id, event_correlation_id = _resolve_action_event_ids(
                            tool_call_id=tool_call_id,
                            tool_arguments=fn_args,
                        )
                        policy_decision = _resolve_integration_policy_for_tool_call(
                            tool_name=fn_name,
                            tool_arguments=fn_args,
                        )
                        policy_payload = _build_policy_payload(policy_decision) if policy_decision is not None else None

                        if policy_decision is not None and not policy_decision.allowed:
                            blocked_reason = policy_decision.reason or "Blocked by integration action policy"
                            blocked_result: dict[str, Any] = {
                                "error": blocked_reason,
                                "policy": policy_payload,
                            }
                            await ws.send_json(
                                _build_chat_action_event(
                                    phase="blocked",
                                    tool=fn_name,
                                    message=f"Tool blocked by policy: {fn_name.replace('_', ' ')}",
                                    action_id=event_action_id,
                                    correlation_id=event_correlation_id,
                                    error=blocked_reason,
                                    result=blocked_result,
                                    policy=policy_payload,
                                )
                            )

                            messages.append({"role": "tool", "content": blocked_result})
                            await ws.send_json(
                                {
                                    "type": "action",
                                    "tool": fn_name,
                                    "result": blocked_result,
                                }
                            )
                            continue

                        await ws.send_json(
                            _build_chat_action_event(
                                phase="proposed",
                                tool=fn_name,
                                message=f"Planned tool call: {fn_name.replace('_', ' ')}",
                                action_id=event_action_id,
                                correlation_id=event_correlation_id,
                                policy=policy_payload,
                            )
                        )
                        await ws.send_json(
                            _build_chat_action_event(
                                phase="executing",
                                tool=fn_name,
                                message=f"Running tool: {fn_name.replace('_', ' ')}",
                                action_id=event_action_id,
                                correlation_id=event_correlation_id,
                                policy=policy_payload,
                            )
                        )

                        try:
                            from app.database import async_session_factory, set_rls_tenant

                            async with async_session_factory() as tool_session:
                                await set_rls_tenant(tool_session, tenant_id)
                                tool_result = await execute_tool(  # type: ignore[assignment]
                                    fn_name,
                                    fn_args,
                                    session=tool_session,
                                    tenant_id=tenant_id,
                                    grow_id=grow_uuid,
                                )
                        except Exception as e:
                            logger.exception("Tool execution error")
                            tool_result = {"error": f"Error: {e}"}  # type: ignore[assignment]
                            await ws.send_json(
                                _build_chat_action_event(
                                    phase="failed",
                                    tool=fn_name,
                                    message=f"Tool failed: {fn_name.replace('_', ' ')}",
                                    action_id=event_action_id,
                                    correlation_id=event_correlation_id,
                                    error=str(e),
                                    policy=policy_payload,
                                )
                            )
                        else:
                            completed_action_id, completed_correlation_id = _resolve_action_event_ids(
                                tool_call_id=tool_call_id,
                                tool_arguments=fn_args,
                                tool_result=tool_result,
                            )
                            await ws.send_json(
                                _build_chat_action_event(
                                    phase="completed",
                                    tool=fn_name,
                                    message=f"Tool completed: {fn_name.replace('_', ' ')}",
                                    action_id=completed_action_id,
                                    correlation_id=completed_correlation_id,
                                    result=tool_result,
                                    policy=policy_payload,
                                )
                            )

                        messages.append({"role": "tool", "content": tool_result})
                        await ws.send_json(
                            {
                                "type": "action",
                                "tool": fn_name,
                                "result": tool_result,
                            }
                        )

            # Stream the final natural-language response
            full_response = ""
            try:
                async for chunk in chat_completion_stream(messages):
                    full_response += chunk
                    await ws.send_json({"type": "chunk", "content": chunk})
            except Exception:
                logger.warning("Ollama stream failed, falling back to Gemini")
                # Fallback to Gemini (non-streaming)
                try:
                    from app.ai.gemini import chat_completion as gemini_chat
                    from app.ai.gemini import is_configured as gemini_configured

                    if not gemini_configured():
                        raise RuntimeError("Gemini not configured")
                    full_response = await gemini_chat(messages)
                    await ws.send_json({"type": "chunk", "content": full_response})
                except Exception:
                    logger.exception("Gemini chat fallback also failed")
                    await ws.send_json({"type": "error", "message": "AI service unavailable"})
                    continue

            messages.append({"role": "assistant", "content": full_response})
            await ws.send_json({"type": "done", "content": full_response})

            # Persist assistant message
            if conv_uuid and full_response:
                try:
                    async with async_session_factory() as session:
                        await set_rls_tenant(session, tenant_id)
                        session.add(
                            ConversationMessage(conversation_id=conv_uuid, role="assistant", content=full_response)
                        )
                        conv = await session.get(Conversation, conv_uuid)
                        if conv:
                            conv.message_count = (conv.message_count or 0) + 1
                            # Auto-title from first user message if untitled
                            if not conv.title and len(messages) >= 3:
                                conv.title = messages[1]["content"][:100]
                        await session.commit()
                except Exception:
                    logger.debug("Failed to persist assistant message")

    except WebSocketDisconnect:
        logger.debug("Chat WebSocket disconnected")
    finally:
        keepalive_stop.set()
        keepalive_task.cancel()
        with suppress(asyncio.CancelledError):
            await keepalive_task


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
    photo_url: str | None = None
    created_at: str | None = None


class HealthCheckHistoryResponse(BaseModel):
    items: list[HealthCheckResponse]


@router.post(
    "/health-check",
    response_model=HealthCheckResponse,
    dependencies=[Depends(require_usage_limit("ai_analyses"))],
)
async def run_health_check(
    body: HealthCheckRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Run AI health check with camera image and full grow data.

    Tries local Ollama vision LLM first, falls back to Gemini if unavailable.
    """
    from app.ai.gemini import (
        GeminiRateLimitError,
    )
    from app.ai.gemini import (
        chat_completion as gemini_chat,
    )
    from app.ai.gemini import (
        is_configured as gemini_configured,
    )
    from app.ai.ollama import vision_diagnose
    from app.grows.models import GrowCycle, HealthEval

    grow = await session.get(GrowCycle, UUID(body.grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    # Gather ALL data (camera may timeout — don't let that block the request)
    try:
        grow_data = await gather_grow_data(
            session,
            grow,
            include_camera=body.include_camera,
        )
    except Exception:
        logger.warning("gather_grow_data failed, retrying without camera")
        grow_data = await gather_grow_data(session, grow, include_camera=False)

    # Build prompt with all data
    messages = await build_health_check_prompt(grow_data, body.observations, session=session)

    # Prepare images
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

    # Try local Ollama vision first, fall back to Gemini
    raw: str | None = None
    if camera_image or body.image_base64:
        # Build a combined text prompt from messages for Ollama
        ollama_prompt = "\n\n".join(m["content"] for m in messages)
        # Use the primary image (prefer user-uploaded, then camera)
        image_b64 = body.image_base64 if body.image_base64 else None
        if not image_b64 and camera_image:
            import base64 as b64mod

            image_b64 = b64mod.b64encode(camera_image).decode()
        if image_b64:
            try:
                raw = await vision_diagnose(image_b64, ollama_prompt)
                logger.info("Health check completed via local Ollama vision")
            except Exception:
                logger.warning("Ollama vision failed for health check, falling back to Gemini")

    if raw is None:
        if not gemini_configured():
            raise HTTPException(status_code=503, detail="AI service unavailable (local and cloud)") from None
        try:
            raw = await gemini_chat(
                messages,
                image_bytes=camera_image,
                extra_images=extra_images or None,
            )
            logger.info("Health check completed via Gemini fallback")
        except GeminiRateLimitError:
            raise HTTPException(
                status_code=429,
                detail="AI rate limit reached. Try again in a few minutes.",
            ) from None
        except Exception:
            logger.exception("Gemini health check also failed")
            raise HTTPException(status_code=503, detail="AI service unavailable") from None

    # Parse JSON response — service helper handles markdown-fence stripping,
    # JSON-decode failures, and the issue/action normalization in one place.
    score, issues, actions = service.parse_health_check_json(raw)
    if score is None and not issues and not actions and raw.strip():
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
    photo_key: str | None = None
    if camera_image:
        try:
            import asyncio

            from app.grows.models import GrowPhoto
            from app.storage import upload_photo as s3_upload

            loop = asyncio.get_running_loop()
            key = await loop.run_in_executor(
                None,
                s3_upload,
                camera_image,
                "image/jpeg",
                str(grow.tenant_id),
                str(grow.id),
            )
            grow_photo = GrowPhoto(
                tenant_id=grow.tenant_id,
                grow_cycle_id=grow.id,
                source="health_check",
                storage_key=key,
                caption=f"Health check snapshot (score: {score})" if score else "Health check snapshot",
            )
            session.add(grow_photo)
            photo_key = key
        except Exception:
            logger.exception("Failed to save health check camera snapshot to S3")

    # Also save user-uploaded image as a grow photo
    if body.image_base64:
        try:
            import asyncio

            from app.grows.models import GrowPhoto
            from app.storage import upload_photo as s3_upload

            user_bytes = base64.b64decode(body.image_base64)
            loop = asyncio.get_running_loop()
            key = await loop.run_in_executor(
                None,
                s3_upload,
                user_bytes,
                "image/jpeg",
                str(grow.tenant_id),
                str(grow.id),
            )
            grow_photo = GrowPhoto(
                tenant_id=grow.tenant_id,
                grow_cycle_id=grow.id,
                source="health_check",
                storage_key=key,
                caption=f"Health check upload (score: {score})" if score else "Health check upload",
            )
            session.add(grow_photo)
            # Prefer user-uploaded photo as the primary
            photo_key = key
        except Exception:
            logger.exception("Failed to save user-uploaded health check image to S3")

    # Link photo to health eval
    if photo_key:
        health_eval.photo_storage_key = photo_key

    await session.commit()
    await session.refresh(health_eval)

    created_task_count = 0
    task_error: str | None = None
    safe_actions, _approval_actions = service.split_health_check_actions_by_safety(actions)

    # Generate fresh tasks from health check actions (cancels old ones first)
    if safe_actions:
        from app.scheduler.task_generator import create_tasks_from_health_eval

        try:
            created_task_count = await create_tasks_from_health_eval(session, grow, score, issues, safe_actions)
        except Exception as exc:
            task_error = str(exc)
            logger.exception("Failed to create tasks from manual health check for grow %s", grow.id)

    if actions:
        try:
            await service.record_health_check_task_actions(
                session,
                tenant_id=grow.tenant_id,
                grow_cycle_id=grow.id,
                requested_by_user_id=user.user_id,
                health_eval_id=health_eval.id,
                score=score,
                issues=issues,
                actions=actions,
                created_task_count=created_task_count,
                task_error=task_error,
            )
        except Exception:
            logger.exception("Failed to record agent action lifecycle for manual health check %s", health_eval.id)

    await record_usage(session, user.tenant_id, "ai_analyses")
    await session.commit()

    # Build photo URL if photo was saved
    photo_url = service.photo_url_for_key(photo_key)

    return HealthCheckResponse(
        id=str(health_eval.id),
        score=score,
        issues=issues,
        actions=actions,
        raw_analysis=raw,
        source="manual",
        photo_url=photo_url,
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
    evals = (await session.execute(service.list_health_evals_query(grow_id=UUID(grow_id), limit=limit))).scalars().all()

    return HealthCheckHistoryResponse(
        items=[
            HealthCheckResponse(
                id=str(e.id),
                score=e.score,
                issues=[service.normalize_health_history_issue(i) for i in (e.issues or [])],
                actions=[service.normalize_health_history_action(a) for a in (e.actions or [])],
                raw_analysis=e.raw_analysis,
                source=e.source,
                photo_url=service.photo_url_for_key(e.photo_storage_key),
                created_at=e.created_at.isoformat(),
            )
            for e in evals
        ]
    )


@router.delete("/health-check/{eval_id}", status_code=204)
async def delete_health_eval(
    eval_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a health evaluation by ID."""
    eval_obj = await service.get_health_eval(session, UUID(eval_id))
    if eval_obj is None:
        raise HTTPException(status_code=404, detail="Health evaluation not found")
    if eval_obj.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Health evaluation not found")
    await session.delete(eval_obj)
    await session.commit()


# ---------- Coach Tips (4.3) ----------


class CoachTipRequest(BaseModel):
    grow_id: str


class CoachTipResponse(BaseModel):
    tip: str


@router.post(
    "/coach-tip",
    response_model=CoachTipResponse,
    dependencies=[Depends(require_usage_limit("ai_analyses"))],
)
async def get_coach_tip(
    body: CoachTipRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get an AI coach tip for a specific grow cycle."""
    from app.grows.models import Bucket, BucketSensorReading, GrowCycle

    grow = await session.get(GrowCycle, UUID(body.grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    sensors = {}
    buckets = (await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow.id))).scalars().all()
    if buckets:
        reading = (
            await session.execute(
                select(BucketSensorReading)
                .where(BucketSensorReading.bucket_id == buckets[0].id)
                .order_by(desc(BucketSensorReading.recorded_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        if reading:
            sensors = {"ph": reading.ph, "ec": reading.ec, "water_temp_f": reading.water_temp_f}

    messages = await build_coach_tip_prompt(grow.grow_type, grow.stage, sensors, session=session)

    try:
        tip = await chat_completion(messages)
    except Exception:
        # Fallback to Gemini if Ollama is unavailable
        try:
            from app.ai.gemini import chat_completion as gemini_chat

            tip = await gemini_chat(messages)
        except Exception:
            raise HTTPException(status_code=503, detail="AI service unavailable") from None

    await record_usage(session, user.tenant_id, "ai_analyses")
    await session.commit()

    return CoachTipResponse(tip=tip.strip())


# ---------- AI Insights (4.13) ----------


class InsightRequest(BaseModel):
    grow_id: str
    insight_type: str  # harvest_predict | nutrient_advice | anomaly_scan


class InsightResponse(BaseModel):
    insight_type: str
    result: dict | str


@router.post(
    "/insights",
    response_model=InsightResponse,
    dependencies=[Depends(require_usage_limit("ai_analyses"))],
)
async def get_insight(
    body: InsightRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get AI-powered insights for a grow cycle."""
    from app.grows.models import Bucket, BucketSensorReading, GrowCycle

    if body.insight_type not in ("harvest_predict", "nutrient_advice", "anomaly_scan"):
        raise HTTPException(status_code=400, detail="Invalid insight type")

    grow = await session.get(GrowCycle, UUID(body.grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    data: dict[str, Any] = {
        "grow_type": grow.grow_type,
        "stage": grow.stage,
        "status": grow.status,
        "started_at": str(grow.started_at),
    }

    # Add sensor summary
    buckets = (await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow.id))).scalars().all()
    if buckets:
        readings = (
            (
                await session.execute(
                    select(BucketSensorReading)
                    .where(BucketSensorReading.bucket_id == buckets[0].id)
                    .order_by(desc(BucketSensorReading.recorded_at))
                    .limit(10)
                )
            )
            .scalars()
            .all()
        )
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

    messages = await build_insight_prompt(body.insight_type, grow.grow_type, data, session=session)

    try:
        raw = await chat_completion(messages)
    except Exception:
        try:
            from app.ai.gemini import chat_completion as gemini_chat

            raw = await gemini_chat(messages)
        except Exception:
            raise HTTPException(status_code=503, detail="AI service unavailable") from None

    # Try to extract JSON from the response (LLM may wrap it in markdown)
    import re

    result: dict | str
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Try to find JSON block in markdown code fence or inline
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if not json_match:
            json_match = re.search(r"(\{.*\})", raw, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                result = raw
        else:
            result = raw

    await record_usage(session, user.tenant_id, "ai_analyses")
    await session.commit()

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
    from datetime import datetime

    from app.grows.models import GrowCycle, HealthEval

    grow = await session.get(GrowCycle, UUID(grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    # Check if we have a valid cache: advice exists and no newer health eval
    if grow.cached_feeding_advice and grow.feeding_advice_cached_at:
        latest_eval = (
            await session.execute(
                select(HealthEval)
                .where(HealthEval.grow_cycle_id == grow.id)
                .order_by(desc(HealthEval.created_at))
                .limit(1)
            )
        ).scalar_one_or_none()

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
    messages = await build_feeding_advice_prompt(grow_data, session=session)

    raw: str | None = None
    try:
        raw = await chat_completion(messages)
    except Exception:
        logger.warning("Ollama failed for feeding advice, trying Gemini")
        try:
            from app.ai.gemini import chat_completion as gemini_chat

            raw = await gemini_chat(messages)
        except Exception:
            logger.exception("Feeding advice AI call failed (both Ollama and Gemini)")

    if raw is None:
        # Both AI providers failed — return stale cache if available
        if grow.cached_feeding_advice:
            cached = grow.cached_feeding_advice
            return FeedingAdviceResponse(
                current_stage_advice=cached.get("current_stage_advice"),
                adjustments=cached.get("adjustments") or [],
                alerts=cached.get("alerts") or [],
                next_transition=cached.get("next_transition"),
                health_impact=cached.get("health_impact"),
            )
        raise HTTPException(status_code=503, detail="AI service unavailable") from None

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
                cleaned = cleaned[start : end + 1]
        parsed = json.loads(cleaned)

        # Cache the parsed result on the grow
        grow.cached_feeding_advice = parsed
        grow.feeding_advice_cached_at = datetime.now(UTC)
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
        raise HTTPException(status_code=404, detail=str(e)) from None

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="grow-report-{grow_id[:8]}.pdf"'},
    )


# ---------- Plant Photo Diagnosis (Gemini Vision) ----------


class DiagnoseRequest(BaseModel):
    image_base64: str
    grow_id: str | None = None
    observations: str | None = None


class DiagnosisIssue(BaseModel):
    name: str
    severity: str  # "low", "medium", "high", "critical"
    confidence: float  # 0-1
    description: str
    treatment: str


class DiagnoseResponse(BaseModel):
    overall_score: int  # 0-100
    summary: str
    issues: list[DiagnosisIssue] = []
    actions: list[str] = []
    grow_stage_assessment: str | None = None


@router.post(
    "/diagnose",
    response_model=DiagnoseResponse,
    dependencies=[Depends(require_usage_limit("ai_analyses"))],
)
async def diagnose_plant_photo(
    body: DiagnoseRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Diagnose plant health from a photo using local vision LLM with Gemini fallback.

    Tries Ollama LLaVA (local, on CPU node) first.
    Falls back to Gemini Vision if local model is unavailable.
    Provides structured issues with severity, confidence, and treatment recommendations.
    Optionally pass grow_id for grow-type-aware diagnosis.
    """
    from app.ai.gemini import (
        GeminiRateLimitError,
    )
    from app.ai.gemini import (
        chat_completion as gemini_chat,
    )
    from app.ai.gemini import (
        is_configured as gemini_configured,
    )
    from app.ai.ollama import vision_diagnose

    try:
        image_bytes = base64.b64decode(body.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data") from None

    # Build grow context if grow_id is provided
    grow_context = ""
    if body.grow_id:
        from app.grows.models import GrowCycle

        grow = await session.get(GrowCycle, UUID(body.grow_id))
        if grow:
            from app.ai.context import get_grow_type_profile_from_db as _get_profile

            profile = await _get_profile(grow.grow_type, session)
            type_name = profile["name"] if profile else grow.grow_type
            common = ", ".join(profile["common_problems"]) if profile else ""
            grow_context = (
                f"\n\nGrow Context:\n"
                f"- Grow type: {type_name}\n"
                f"- Current stage: {grow.stage}\n"
                f"- Common problems for this type: {common}\n"
                f"- Use this context to provide grow-type-specific treatment recommendations.\n"
            )

    observations_text = ""
    if body.observations:
        observations_text = f"\n\nGrower's observations: {body.observations}"

    system_prompt = (
        "You are an expert cannabis plant health diagnostic AI with extensive knowledge of "
        "nutrient deficiencies, pests, diseases, environmental stress, and growth abnormalities. "
        "Analyze the provided plant photo and diagnose any health issues.\n\n"
        "ACCURACY IS CRITICAL:\n"
        "- Only report issues you can clearly identify in the image.\n"
        "- Assign confidence scores honestly — if you're uncertain, reflect that.\n"
        "- If the plant looks healthy, say so. Don't invent problems.\n"
        "- Distinguish between confirmed issues (clearly visible) and potential concerns.\n\n"
        "DIAGNOSTIC AREAS:\n"
        "- Nutrient deficiencies/toxicities (N, P, K, Ca, Mg, Fe, Mn, Zn, S, B, Cu, Mo)\n"
        "- pH-related lockout symptoms\n"
        "- Pests (spider mites, thrips, aphids, fungus gnats, whiteflies, caterpillars)\n"
        "- Diseases (powdery mildew, botrytis/bud rot, root rot, fusarium, septoria)\n"
        "- Environmental stress (light burn, heat stress, wind burn, overwatering, underwatering)\n"
        "- Training/mechanical damage\n"
        f"{grow_context}{observations_text}\n\n"
        "Respond ONLY with valid JSON (no markdown, no code fences):\n"
        "{\n"
        '  "overall_score": <int 0-100>,\n'
        '  "summary": "<1-2 sentence overall assessment>",\n'
        '  "issues": [\n'
        "    {\n"
        '      "name": "<issue name, e.g. Calcium Deficiency>",\n'
        '      "severity": "<low|medium|high|critical>",\n'
        '      "confidence": <float 0.0-1.0>,\n'
        '      "description": "<what you see and why you think this>",\n'
        '      "treatment": "<specific actionable fix>"\n'
        "    }\n"
        "  ],\n"
        '  "actions": ["<immediate action 1>", "<action 2>", ...],\n'
        '  "grow_stage_assessment": "<assessment of growth stage if determinable, or null>"\n'
        "}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please analyze this plant photo and provide a full health diagnosis."},
    ]

    # Try local Ollama vision first, fall back to Gemini
    raw: str | None = None
    try:
        diagnosis_prompt = f"{system_prompt}\n\nPlease analyze this plant photo and provide a full health diagnosis."
        raw = await vision_diagnose(body.image_base64, diagnosis_prompt)
        logger.info("Diagnose completed via local Ollama vision")
    except Exception:
        logger.warning("Ollama vision failed for diagnose, falling back to Gemini")
        if not gemini_configured():
            raise HTTPException(status_code=503, detail="AI service unavailable (local and cloud)") from None
        try:
            raw = await gemini_chat(messages, image_bytes=image_bytes)
            logger.info("Diagnose completed via Gemini fallback")
        except GeminiRateLimitError:
            raise HTTPException(status_code=429, detail="AI rate limit reached. Try again in a few minutes.") from None
        except Exception:
            logger.exception("Gemini diagnose also failed")
            raise HTTPException(status_code=503, detail="AI service unavailable") from None

    # Parse response
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Gemini diagnose returned non-JSON: %s", raw[:300])
        return DiagnoseResponse(
            overall_score=0,
            summary="Unable to parse AI response. Please try again.",
            issues=[],
            actions=[],
        )

    # Save photo as a grow photo if grow_id provided
    if body.grow_id:
        try:
            import asyncio

            from app.grows.models import GrowCycle, GrowPhoto
            from app.storage import upload_photo as s3_upload

            grow = await session.get(GrowCycle, UUID(body.grow_id))
            if grow:
                loop = asyncio.get_running_loop()
                key = await loop.run_in_executor(
                    None,
                    s3_upload,
                    image_bytes,
                    "image/jpeg",
                    str(grow.tenant_id),
                    str(grow.id),
                )
                score = parsed.get("overall_score")
                photo = GrowPhoto(
                    tenant_id=grow.tenant_id,
                    grow_cycle_id=grow.id,
                    source="health_check",
                    storage_key=key,
                    caption=f"AI Diagnosis (score: {score})" if score else "AI Diagnosis",
                )
                session.add(photo)
                await session.commit()
        except Exception:
            logger.exception("Failed to save diagnosis photo to S3")

    await record_usage(session, user.tenant_id, "ai_analyses")
    await session.commit()

    # Safely parse issues — AI may return unexpected dict shapes
    diagnosis_issues: list[DiagnosisIssue] = []
    for i in parsed.get("issues", []):
        if not isinstance(i, dict):
            continue
        try:
            diagnosis_issues.append(DiagnosisIssue(**i))
        except Exception:
            # Partial issue — extract what we can
            diagnosis_issues.append(
                DiagnosisIssue(
                    name=i.get("name", "Unknown Issue"),
                    severity=i.get("severity", "medium"),
                    confidence=float(i.get("confidence", 0.5)),
                    description=i.get("description", str(i)),
                    treatment=i.get("treatment", "Consult detailed diagnosis."),
                )
            )

    # Normalize actions to strings
    raw_actions = parsed.get("actions", [])
    actions_list = [
        a if isinstance(a, str) else (a.get("action") or a.get("message") or a.get("description") or str(a))
        for a in raw_actions
    ]

    return DiagnoseResponse(
        overall_score=parsed.get("overall_score", 0),
        summary=parsed.get("summary", ""),
        issues=diagnosis_issues,
        actions=actions_list,
        grow_stage_assessment=parsed.get("grow_stage_assessment"),
    )


# ---------- Plant Identification (Gemini Vision) ----------


class IdentifyRequest(BaseModel):
    image_base64: str


class IdentifyResponse(BaseModel):
    plant_type: str
    confidence: float
    species: str | None = None
    strain_guess: str | None = None
    strain_confidence: float | None = None
    characteristics: list[str] = []
    growth_stage: str | None = None
    indica_sativa_ratio: str | None = None
    notes: str = ""


@router.post(
    "/identify",
    response_model=IdentifyResponse,
    dependencies=[Depends(require_usage_limit("ai_analyses"))],
)
async def identify_plant(
    body: IdentifyRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Identify a plant from a photo using Gemini Vision.

    Attempts to determine species, possible strain characteristics,
    growth stage, and indica/sativa dominance from visual features.
    """
    from app.ai.gemini import (
        GeminiRateLimitError,
    )
    from app.ai.gemini import (
        chat_completion as gemini_chat,
    )
    from app.ai.gemini import (
        is_configured as gemini_configured,
    )
    from app.ai.ollama import vision_diagnose

    try:
        image_bytes = base64.b64decode(body.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data") from None

    system_prompt = (
        "You are an expert botanist specializing in cannabis (Cannabis sativa L.) identification. "
        "Analyze the provided plant photo and identify the plant.\n\n"
        "IDENTIFICATION CAPABILITIES:\n"
        "- Determine if the plant is cannabis vs another species\n"
        "- Assess indica vs sativa dominance from leaf morphology (broad vs narrow leaves, "
        "internodal spacing, plant structure)\n"
        "- Estimate growth stage (seedling, veg, pre-flower, flower, late flower)\n"
        "- Note distinguishing characteristics (leaf shape, color, structure, trichome density)\n\n"
        "STRAIN IDENTIFICATION LIMITATIONS (be honest):\n"
        "- Visual strain identification is unreliable — there are thousands of strains "
        "with overlapping phenotypes\n"
        "- At best you can suggest indica/sativa dominance and general phenotype characteristics\n"
        "- Purple coloring, leaf shape, bud structure, and growth pattern can narrow down lineage\n"
        "- Never claim 100% certainty on strain identification\n"
        "- If you recognize very distinctive phenotypes (e.g., extreme purple, duck foot, ABC), note them\n\n"
        "ACCURACY:\n"
        "- If the image is not a cannabis plant, say so clearly\n"
        "- If you cannot determine something, set confidence appropriately low or use null\n"
        "- Confidence scores should reflect genuine certainty\n\n"
        "Respond ONLY with valid JSON (no markdown, no code fences):\n"
        "{\n"
        '  "plant_type": "<Cannabis / Not Cannabis / Unknown>",\n'
        '  "confidence": <float 0.0-1.0 for plant_type identification>,\n'
        '  "species": "<Cannabis sativa / Cannabis indica / Hybrid or null>",\n'
        '  "strain_guess": "<best guess strain name or lineage family, or null if impossible to tell>",\n'
        '  "strain_confidence": <float 0.0-1.0 or null — typically low (0.1-0.3) since visual ID is unreliable>,\n'
        '  "characteristics": ["<observable trait 1>", "<trait 2>", ...],\n'
        '  "growth_stage": "<seedling|early_veg|late_veg|pre_flower|early_flower|'
        'mid_flower|late_flower|harvest or null>",\n'
        '  "indica_sativa_ratio": "<e.g. 70% Indica / 30% Sativa, or null if unclear>",\n'
        '  "notes": "<any additional observations about the plant morphology, health, or unusual features>"\n'
        "}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please identify this plant and describe its characteristics."},
    ]

    # Try local Ollama vision first, fall back to Gemini
    raw: str | None = None
    try:
        identify_prompt = f"{system_prompt}\n\nPlease identify this plant and describe its characteristics."
        raw = await vision_diagnose(body.image_base64, identify_prompt)
        logger.info("Identify completed via local Ollama vision")
    except Exception:
        logger.warning("Ollama vision failed for identify, falling back to Gemini")

    if raw is None:
        if not gemini_configured():
            raise HTTPException(status_code=503, detail="AI service unavailable (local and cloud)") from None
        try:
            raw = await gemini_chat(messages, image_bytes=image_bytes)
            logger.info("Identify completed via Gemini fallback")
        except GeminiRateLimitError:
            raise HTTPException(status_code=429, detail="AI rate limit reached. Try again in a few minutes.") from None
        except Exception:
            logger.exception("Gemini identify also failed")
            raise HTTPException(status_code=503, detail="AI service unavailable") from None

    # Parse response
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Gemini identify returned non-JSON: %s", raw[:300])
        await record_usage(session, user.tenant_id, "ai_analyses")
        await session.commit()
        return IdentifyResponse(
            plant_type="Unknown",
            confidence=0.0,
            notes="Unable to parse AI response. Please try again.",
        )

    await record_usage(session, user.tenant_id, "ai_analyses")
    await session.commit()

    return IdentifyResponse(
        plant_type=parsed.get("plant_type", "Unknown"),
        confidence=parsed.get("confidence", 0.0),
        species=parsed.get("species"),
        strain_guess=parsed.get("strain_guess"),
        strain_confidence=parsed.get("strain_confidence"),
        characteristics=parsed.get("characteristics", []),
        growth_stage=parsed.get("growth_stage"),
        indica_sativa_ratio=parsed.get("indica_sativa_ratio"),
        notes=parsed.get("notes", ""),
    )


# ---------- Treatment Recommendations Database ----------


class TreatmentSummaryResponse(BaseModel):
    id: str
    category: str
    name: str
    summary: str


class TreatmentDetailResponse(BaseModel):
    id: str
    category: str
    name: str
    aka: list[str]
    summary: str
    symptoms: list[str]
    identification_tips: list[str]
    causes: list[str]
    severity_criteria: dict[str, str]
    treatments: dict[str, list[str]]
    prevention: list[str]
    recovery_time: str
    commonly_confused_with: list[str]


class TreatmentListResponse(BaseModel):
    items: list[TreatmentSummaryResponse]
    total: int


@router.get("/treatments", response_model=TreatmentListResponse)
async def list_treatments(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    category: str | None = None,
    query: str | None = None,
):
    """List treatment database entries, optionally filtered by category or search query."""
    from app.config_management.service.treatments import (
        list_all,
    )
    from app.config_management.service.treatments import (
        list_by_category as db_list_by_category,
    )
    from app.config_management.service.treatments import (
        search_treatments as db_search,
    )

    if query:
        entries = await db_search(session, query)
    elif category:
        entries = await db_list_by_category(session, category)
    else:
        entries = await list_all(session)

    return TreatmentListResponse(
        items=[
            TreatmentSummaryResponse(id=e["id"], category=e["category"], name=e["name"], summary=e["summary"])
            for e in entries
        ],
        total=len(entries),
    )


@router.get("/treatments/{treatment_id}", response_model=TreatmentDetailResponse)
async def get_treatment_detail(
    treatment_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_type: str | None = None,
):
    """Get detailed treatment information for a specific issue.

    Optionally pass grow_type to get type-specific treatment recommendations.
    """
    from app.config_management.service.treatments import get_treatment as db_get_treatment

    entry = await db_get_treatment(session, treatment_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Treatment not found")

    treatments = dict(entry.get("treatments", {}))
    if grow_type and grow_type in treatments:
        treatments = {grow_type: treatments[grow_type]}

    return TreatmentDetailResponse(
        id=entry["id"],
        category=entry["category"],
        name=entry["name"],
        aka=entry["aka"],
        summary=entry["summary"],
        symptoms=entry["symptoms"],
        identification_tips=entry["identification_tips"],
        causes=entry["causes"],
        severity_criteria=entry["severity_criteria"],
        treatments=treatments,
        prevention=entry["prevention"],
        recovery_time=entry["recovery_time"],
        commonly_confused_with=entry["commonly_confused_with"],
    )
