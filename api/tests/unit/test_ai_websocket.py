"""Unit tests for AI websocket event helpers."""

from __future__ import annotations

from datetime import datetime

from app.ai.routes import _build_chat_action_event, _build_keepalive_event


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
            result={"status": "ok"},
        )

        assert event == {
            "type": "action_event",
            "phase": "completed",
            "tool": "update_grow_stage",
            "message": "Tool completed: update grow stage",
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

        assert "result" not in event
        assert "error" not in event
