"""Unit tests for AI websocket event helpers."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.ai.models import AgentAction
from app.ai.routes import (
    _build_chat_action_event,
    _build_keepalive_event,
    _extract_action_id_from_tool_arguments,
    _extract_action_id_from_tool_result,
    _extract_integration_type_from_tool_arguments,
    _extract_policy_payload_from_tool_result,
    _extract_tool_result_error,
    _resolve_action_event_ids,
    _resolve_action_event_phase,
    _resolve_integration_policy_for_tool_call,
    websocket_chat,
)
from app.commercial.models import Task
from tests.conftest import TenantFactory


class FakeWebSocket:
    def __init__(self, incoming: list[dict[str, object]]):
        self._incoming = incoming
        self.sent: list[dict[str, object]] = []
        self.cookies: dict[str, str] = {}
        self.accepted = False
        self.closed = False

    async def accept(self) -> None:
        self.accepted = True

    async def receive_json(self) -> dict[str, object]:
        if self._incoming:
            return self._incoming.pop(0)

        from fastapi import WebSocketDisconnect

        raise WebSocketDisconnect()

    async def send_json(self, payload: dict[str, object]) -> None:
        self.sent.append(payload)

    async def close(self) -> None:
        self.closed = True


async def _create_grow(session, *, tenant_id):
    from app.grows.models import GrowCycle, Tent

    tent = Tent(
        tenant_id=tenant_id,
        name="Websocket Test Tent",
    )
    session.add(tent)
    await session.flush()

    grow = GrowCycle(
        tenant_id=tenant_id,
        tent_id=tent.id,
        name="Websocket Test Grow",
        grow_type="dwc",
        stage="vegetative",
    )
    session.add(grow)
    await session.commit()
    await session.refresh(grow)
    return grow


async def _run_websocket_chat_once(
    *,
    tenant: dict,
    grow_id: str,
    tool_call: dict[str, object],
    final_chunks: list[str],
) -> FakeWebSocket:
    payload = {"type": "access", "tid": str(tenant["tenant"].id), "sub": str(tenant["user"].id)}
    websocket = FakeWebSocket(
        [
            {"token": "test-token", "grow_id": grow_id},
            {"message": "Please handle this safely."},
        ]
    )

    async def fake_stream(_messages):
        for chunk in final_chunks:
            yield chunk

    with patch("app.ai.routes.decode_token", return_value=payload), patch(
        "app.ai.routes.gather_grow_data", new=AsyncMock(return_value={"grow_id": grow_id})
    ), patch("app.ai.routes.build_chat_context", new=AsyncMock(return_value="You are Tendril.")), patch(
        "app.ai.routes.chat_with_tools",
        new=AsyncMock(
            side_effect=[
                {
                    "content": "",
                    "tool_calls": [tool_call],
                    "message": {"role": "assistant", "content": "", "tool_calls": [tool_call]},
                },
                {
                    "content": "Checklist complete.",
                    "tool_calls": None,
                    "message": {"role": "assistant", "content": "Checklist complete."},
                },
            ]
        ),
    ), patch("app.ai.routes.chat_completion_stream", fake_stream):
        await websocket_chat(websocket)

    return websocket


class TestAiWebsocketEventHelpers:
    def test_build_keepalive_event_has_ping_type_and_timestamp(self):
        event = _build_keepalive_event()

        assert event["type"] == "ping"
        assert isinstance(datetime.fromisoformat(event["ts"]), datetime)

    def test_build_chat_action_event_includes_phase_refresh_and_payload(self):
        event = _build_chat_action_event(
            phase="completed",
            tool="update_grow_stage",
            message="Tool completed: update grow stage",
            action_id="tool-call-1",
            correlation_id="corr-1",
            result={"status": "ok"},
        )

        assert event == {
            "type": "action_event",
            "phase": "completed",
            "tool": "update_grow_stage",
            "message": "Tool completed: update grow stage",
            "action_id": "tool-call-1",
            "correlation_id": "corr-1",
            "refresh_actions": True,
            "result": {"status": "ok"},
            "ts": event["ts"],
        }
        assert isinstance(datetime.fromisoformat(event["ts"]), datetime)

    def test_build_chat_action_event_omits_optional_keys_when_absent(self):
        event = _build_chat_action_event(
            phase="executing",
            tool="update_grow_stage",
            message="Running tool",
        )

        assert "action_id" not in event
        assert "correlation_id" not in event
        assert "result" not in event
        assert "error" not in event
        assert "policy" not in event

    def test_build_chat_action_event_includes_optional_policy_payload(self):
        event = _build_chat_action_event(
            phase="blocked",
            tool="integration_trigger_sync",
            message="Tool blocked by policy",
            policy={"integration_type": "tuya", "allowed": False},
        )

        assert event["policy"] == {"integration_type": "tuya", "allowed": False}

    def test_extract_action_id_from_tool_result_prefers_action_id(self):
        assert _extract_action_id_from_tool_result({"action_id": "action-123", "agent_action_id": "legacy-1"}) == "action-123"

    def test_extract_action_id_from_tool_result_uses_agent_action_id_fallback(self):
        assert _extract_action_id_from_tool_result({"agent_action_id": "legacy-1"}) == "legacy-1"

    def test_extract_action_id_from_tool_result_ignores_non_dict(self):
        assert _extract_action_id_from_tool_result("ok") is None

    def test_extract_policy_payload_from_tool_result_returns_policy_dict(self):
        payload = _extract_policy_payload_from_tool_result({"policy": {"allowed": False, "reason": "Denied"}})
        assert payload == {"allowed": False, "reason": "Denied"}

    def test_extract_policy_payload_from_tool_result_ignores_non_dict(self):
        assert _extract_policy_payload_from_tool_result("ok") is None

    def test_resolve_action_event_phase_reads_blocked_from_tool_result(self):
        assert _resolve_action_event_phase({"phase": "blocked"}) == "blocked"

    def test_resolve_action_event_phase_reads_pending_approval_from_tool_result(self):
        assert _resolve_action_event_phase({"phase": "pending_approval"}) == "pending_approval"

    def test_resolve_action_event_phase_defaults_to_completed(self):
        assert _resolve_action_event_phase({"status": "ok"}) == "completed"

    def test_extract_tool_result_error_reads_error_string(self):
        assert _extract_tool_result_error({"error": "Policy denied"}) == "Policy denied"

    def test_extract_tool_result_error_returns_none_without_error(self):
        assert _extract_tool_result_error({"status": "ok"}) is None

    def test_extract_action_id_from_tool_arguments_prefers_action_id(self):
        assert _extract_action_id_from_tool_arguments({"action_id": "action-456", "agent_action_id": "legacy-1"}) == "action-456"

    def test_extract_action_id_from_tool_arguments_uses_agent_action_id_fallback(self):
        assert _extract_action_id_from_tool_arguments({"agent_action_id": "legacy-1"}) == "legacy-1"

    def test_extract_action_id_from_tool_arguments_ignores_non_dict(self):
        assert _extract_action_id_from_tool_arguments("ok") is None

    def test_extract_integration_type_from_tool_arguments_prefers_integration_type(self):
        assert _extract_integration_type_from_tool_arguments({"integration_type": "Pulse"}) == "Pulse"

    def test_extract_integration_type_from_tool_arguments_falls_back_to_connector(self):
        assert _extract_integration_type_from_tool_arguments({"connector": "ecowitt"}) == "ecowitt"

    def test_extract_integration_type_from_tool_arguments_ignores_non_dict(self):
        assert _extract_integration_type_from_tool_arguments("nope") is None

    def test_resolve_integration_policy_for_tool_call_unsupported_connector_blocked(self):
        decision = _resolve_integration_policy_for_tool_call(
            tool_name="integration_trigger_sync",
            tool_arguments={"integration_type": "tuya"},
        )

        assert decision is not None
        assert decision.allowed is False
        assert decision.supported is False
        assert decision.reason == "Unsupported integration connector: tuya"

    def test_resolve_integration_policy_for_tool_call_non_integration_tool_returns_none(self):
        decision = _resolve_integration_policy_for_tool_call(
            tool_name="update_grow_stage",
            tool_arguments={"integration_type": "pulse"},
        )

        assert decision is None

    def test_resolve_integration_policy_for_control_command_maps_to_outbound_control(self):
        decision = _resolve_integration_policy_for_tool_call(
            tool_name="integration_control_command",
            tool_arguments={"integration_type": "pulse"},
        )

        assert decision is not None
        assert decision.operation == "outbound_control"
        assert decision.risk_level == "high"

    def test_resolve_action_event_ids_prefers_result_then_args_then_correlation(self):
        action_id, correlation_id = _resolve_action_event_ids(
            tool_call_id="tool-call-3",
            tool_arguments={"action_id": "action-from-args"},
            tool_result={"action_id": "action-from-result"},
        )

        assert action_id == "action-from-result"
        assert correlation_id == "tool-call-3"

    def test_resolve_action_event_ids_uses_args_when_result_missing(self):
        action_id, correlation_id = _resolve_action_event_ids(
            tool_call_id="tool-call-4",
            tool_arguments={"agent_action_id": "action-from-args"},
        )

        assert action_id == "action-from-args"
        assert correlation_id == "tool-call-4"

    def test_resolve_action_event_ids_falls_back_to_correlation(self):
        action_id, correlation_id = _resolve_action_event_ids(
            tool_call_id="tool-call-5",
            tool_arguments={},
            tool_result={},
        )

        assert action_id == "tool-call-5"
        assert correlation_id == "tool-call-5"


class TestAiWebsocketChatTools:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_websocket_chat_emits_safe_create_task_lifecycle(self, db_session):
        tenant = await TenantFactory(db_session).create(plan="commercial")
        grow = await _create_grow(db_session, tenant_id=tenant["tenant"].id)

        websocket = await _run_websocket_chat_once(
            tenant=tenant,
            grow_id=str(grow.id),
            tool_call={
                "id": "tool-call-task-1",
                "function": {
                    "name": "create_task",
                    "arguments": {
                        "title": "Calibrate pH pen",
                        "description": "Use fresh 7.0 solution before tomorrow morning.",
                        "priority": "high",
                    },
                },
            },
            final_chunks=["Created the task and logged it in the queue."],
        )

        assert websocket.accepted is True
        assert any(event.get("type") == "ready" for event in websocket.sent)
        assert any(event.get("type") == "conversation_id" for event in websocket.sent)

        action_events = [event for event in websocket.sent if event.get("type") == "action_event"]
        assert [event["phase"] for event in action_events] == ["proposed", "executing", "completed"]
        assert action_events[-1]["result"]["status"] == "completed"
        assert action_events[-1]["tool"] == "create_task"

        action_payloads = [event for event in websocket.sent if event.get("type") == "action"]
        assert action_payloads[-1]["tool"] == "create_task"
        assert action_payloads[-1]["result"]["result"]["title"] == "Calibrate pH pen"

        done_event = next(event for event in websocket.sent if event.get("type") == "done")
        assert done_event["content"] == "Created the task and logged it in the queue."

        task = (
            await db_session.execute(
                select(Task).where(Task.grow_cycle_id == grow.id, Task.title == "Calibrate pH pen")
            )
        ).scalar_one()
        assert task.priority == "high"
        assert task.source == "ai"

        action = (
            await db_session.execute(
                select(AgentAction).where(AgentAction.grow_cycle_id == grow.id, AgentAction.action_type == "create_task")
            )
        ).scalar_one()
        assert action.status == "verified"
        assert action.auto_approved is True
        assert action.verification_json["result"] == "task_created"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_websocket_chat_emits_safe_generate_checklist_lifecycle(self, db_session):
        tenant = await TenantFactory(db_session).create(plan="commercial")
        grow = await _create_grow(db_session, tenant_id=tenant["tenant"].id)

        websocket = await _run_websocket_chat_once(
            tenant=tenant,
            grow_id=str(grow.id),
            tool_call={
                "id": "tool-call-checklist-1",
                "function": {
                    "name": "generate_checklist",
                    "arguments": {
                        "title": "Pre-flip prep",
                        "items": [
                            "Inspect trellis anchors",
                            "Top off reservoir",
                            "Document canopy height",
                        ],
                        "priority": "medium",
                        "category": "prep_checklist",
                    },
                },
            },
            final_chunks=["I turned that checklist into three follow-up tasks."],
        )

        action_events = [event for event in websocket.sent if event.get("type") == "action_event"]
        assert [event["phase"] for event in action_events] == ["proposed", "executing", "completed"]
        assert action_events[-1]["tool"] == "generate_checklist"
        assert action_events[-1]["result"]["result"]["task_count"] == 3

        task_titles = (
            await db_session.execute(
                select(Task.title).where(Task.grow_cycle_id == grow.id).order_by(Task.created_at.asc())
            )
        ).scalars().all()
        assert task_titles == [
            "Inspect trellis anchors",
            "Top off reservoir",
            "Document canopy height",
        ]

        action = (
            await db_session.execute(
                select(AgentAction).where(
                    AgentAction.grow_cycle_id == grow.id,
                    AgentAction.action_type == "generate_checklist",
                )
            )
        ).scalar_one()
        assert action.status == "verified"
        assert action.verification_json["result"] == "checklist_created"
        assert action.verification_json["task_count"] == 3
