"""Unit tests for AI integration action policy helpers."""

from app.ai.integration_policy import (
    SUPPORTED_INTEGRATION_TYPES,
    evaluate_integration_action_policy,
)


class TestIntegrationActionPolicy:
    def test_supported_connector_coverage_includes_phase1_targets(self):
        assert "pulse" in SUPPORTED_INTEGRATION_TYPES
        assert "openweather" in SUPPORTED_INTEGRATION_TYPES
        assert "ecowitt" in SUPPORTED_INTEGRATION_TYPES

    def test_low_risk_operation_is_allowed_without_simulation(self):
        decision = evaluate_integration_action_policy(
            integration_type="openweather",
            operation="poll",
        )

        assert decision.supported is True
        assert decision.allowed is True
        assert decision.risk_level == "low"
        assert decision.requires_approval is False
        assert decision.requires_simulation is False
        assert decision.reason is None

    def test_high_risk_outbound_control_requires_approval_and_simulation(self):
        decision = evaluate_integration_action_policy(
            integration_type="pulse",
            operation="outbound_control",
        )

        assert decision.supported is True
        assert decision.allowed is True
        assert decision.risk_level == "high"
        assert decision.requires_approval is True
        assert decision.requires_simulation is True

    def test_blocked_by_tenant_policy_when_operation_not_allowlisted(self):
        decision = evaluate_integration_action_policy(
            integration_type="ecowitt",
            operation="outbound_control",
            allowlist_policy={"ecowitt": {"poll"}},
        )

        assert decision.supported is True
        assert decision.allowed is False
        assert decision.reason == "Blocked by tenant integration policy: ecowitt.outbound_control"

    def test_unsupported_connector_is_blocked(self):
        decision = evaluate_integration_action_policy(
            integration_type="tuya",
            operation="outbound_control",
        )

        assert decision.supported is False
        assert decision.allowed is False
        assert decision.risk_level == "high"
        assert decision.requires_approval is True
        assert decision.requires_simulation is True
        assert decision.reason == "Unsupported integration connector: tuya"
