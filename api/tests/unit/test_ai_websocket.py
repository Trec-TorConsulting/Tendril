"""Unit tests for AI websocket event helpers."""

from __future__ import annotations

from datetime import datetime

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
)


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
