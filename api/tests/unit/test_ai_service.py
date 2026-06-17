"""Unit tests for app.ai.service pure helpers."""

from __future__ import annotations

import base64
from uuid import UUID, uuid4

import pytest

from app.ai.service import (
    DEFAULT_DIAGNOSIS_OVERALL_SCORE,
    DEFAULT_DIAGNOSIS_OVERALL_SEVERITY,
    DIAGNOSIS_SYSTEM_PROMPT,
    HEALTH_HISTORY_MAX_LIMIT,
    MAX_DIAGNOSE_IMAGE_BYTES,
    DiagnoseImageError,
    build_diagnosis_prompt,
    decode_diagnose_image,
    normalize_health_action,
    normalize_health_history_action,
    normalize_health_history_issue,
    normalize_health_issue,
    parse_diagnosis_response,
    parse_health_check_json,
    parse_optional_uuid,
)


class TestParseOptionalUuid:
    def test_none_returns_none(self):
        assert parse_optional_uuid(None) is None

    def test_empty_string_returns_none(self):
        # The route accepts an absent query param as None and an empty
        # string from form-encoded inputs the same way.
        assert parse_optional_uuid("") is None

    def test_valid_uuid_round_trips(self):
        u = uuid4()
        assert parse_optional_uuid(str(u)) == u

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_optional_uuid("not-a-uuid")

    def test_partial_uuid_raises(self):
        with pytest.raises(ValueError):
            parse_optional_uuid("12345")

    def test_canonical_lowercase_hex(self):
        # Canonical UUID string form is accepted as-is.
        u = UUID("12345678-1234-5678-1234-567812345678")
        assert parse_optional_uuid("12345678-1234-5678-1234-567812345678") == u


# ---------- Diagnose service helpers ----------


class TestDecodeDiagnoseImage:
    def test_valid_image_round_trips(self):
        # Tiny 1x1 PNG-ish payload
        payload = b"\x89PNG\r\n\x1a\nfake"
        b64 = base64.b64encode(payload).decode()
        assert decode_diagnose_image(b64) == payload

    def test_invalid_base64_raises(self):
        with pytest.raises(DiagnoseImageError, match="Invalid base64"):
            decode_diagnose_image("not valid base64!!!")

    def test_oversize_raises(self):
        # Build a payload that bcrypt-style decodes to > MAX bytes
        payload = b"x" * (MAX_DIAGNOSE_IMAGE_BYTES + 1)
        b64 = base64.b64encode(payload).decode()
        with pytest.raises(DiagnoseImageError, match="exceeds"):
            decode_diagnose_image(b64)

    def test_size_cap_documented(self):
        # 10 MiB matches multipart limits across the stack — guard against drift.
        assert MAX_DIAGNOSE_IMAGE_BYTES == 10 * 1024 * 1024


class TestBuildDiagnosisPrompt:
    def test_no_context_returns_base_prompt_plus_instruction(self):
        out = build_diagnosis_prompt()
        assert DIAGNOSIS_SYSTEM_PROMPT in out
        assert "Analyze the photo and provide your diagnosis as JSON." in out
        # No context block
        assert "Context:" not in out

    def test_grow_type_only(self):
        out = build_diagnosis_prompt(grow_type="dwc")
        assert "Context:" in out
        assert "Grow method: dwc" in out
        assert "Current stage:" not in out

    def test_all_context_fields(self):
        out = build_diagnosis_prompt(
            grow_type="coco",
            current_stage="flowering",
            observations="Yellow tips on lower fans",
        )
        assert "Grow method: coco" in out
        assert "Current stage: flowering" in out
        assert "Grower observations: Yellow tips on lower fans" in out

    def test_empty_strings_treated_as_falsy(self):
        out = build_diagnosis_prompt(grow_type="", current_stage="", observations="")
        # Empty strings → no context block
        assert "Context:" not in out


class TestParseDiagnosisResponse:
    def test_valid_json_round_trip(self):
        raw = (
            '{"summary": "Plant looks healthy", '
            '"recommended_actions": ["water tomorrow"], '
            '"overall_severity": "low", "overall_score": 95, '
            '"grow_stage_assessment": "Mid veg", "issues": []}'
        )
        parsed = parse_diagnosis_response(raw)
        assert parsed.summary == "Plant looks healthy"
        assert parsed.actions == ["water tomorrow"]
        assert parsed.overall_severity == "low"
        assert parsed.overall_score == 95
        assert parsed.grow_stage_assessment == "Mid veg"
        assert parsed.issues == []

    def test_issues_parsed(self):
        raw = (
            '{"summary": "x", "recommended_actions": [], '
            '"overall_severity": "high", "overall_score": 60, '
            '"grow_stage_assessment": null, '
            '"issues": [{"treatment_id": "nitrogen_deficiency", '
            '"name": "N def", "confidence": 0.92, "severity": "high", '
            '"description": "yellowing", "treatment": "feed N"}]}'
        )
        parsed = parse_diagnosis_response(raw)
        assert len(parsed.issues) == 1
        i = parsed.issues[0]
        assert i.treatment_id == "nitrogen_deficiency"
        assert i.confidence == 0.92
        assert i.severity == "high"

    def test_confidence_clamped_to_0_1(self):
        raw = (
            '{"summary": "x", "recommended_actions": [], '
            '"overall_severity": "low", "overall_score": 100, '
            '"grow_stage_assessment": null, '
            '"issues": [{"treatment_id": "t", "name": "n", '
            '"confidence": 1.5, "severity": "low"}, '
            '{"treatment_id": "u", "name": "m", '
            '"confidence": -0.3, "severity": "low"}]}'
        )
        parsed = parse_diagnosis_response(raw)
        assert parsed.issues[0].confidence == 1.0
        assert parsed.issues[1].confidence == 0.0

    def test_strips_markdown_fence(self):
        raw = '```json\n{"summary": "fenced", "recommended_actions": [], "overall_severity": "low", "overall_score": 50, "grow_stage_assessment": null, "issues": []}\n```'
        parsed = parse_diagnosis_response(raw)
        assert parsed.summary == "fenced"

    def test_invalid_json_falls_back_to_raw_summary(self):
        parsed = parse_diagnosis_response("not json at all")
        assert parsed.summary == "not json at all"
        assert parsed.overall_severity == DEFAULT_DIAGNOSIS_OVERALL_SEVERITY
        assert parsed.overall_score == DEFAULT_DIAGNOSIS_OVERALL_SCORE
        assert parsed.issues == []

    def test_empty_string_falls_back(self):
        parsed = parse_diagnosis_response("")
        # Documented placeholder when there's no raw text either.
        assert parsed.summary == "Diagnosis could not be parsed"

    def test_long_invalid_response_truncated_to_500(self):
        long_raw = "x" * 1000
        parsed = parse_diagnosis_response(long_raw)
        assert len(parsed.summary) == 500


# ---------- Health-check service helpers ----------


class TestNormalizeHealthIssue:
    def test_string_passes_through(self):
        assert normalize_health_issue("Leaves yellowing") == "Leaves yellowing"

    def test_dict_description(self):
        assert normalize_health_issue({"description": "Nitrogen def"}) == "Nitrogen def"

    def test_dict_message_fallback(self):
        assert normalize_health_issue({"message": "Low EC"}) == "Low EC"

    def test_dict_issue_fallback(self):
        assert normalize_health_issue({"issue": "Light burn"}) == "Light burn"

    def test_dict_with_category_prefix(self):
        out = normalize_health_issue({"description": "Yellowing", "category": "Nutrient"})
        assert out == "[Nutrient] Yellowing"

    def test_dict_no_recognized_keys_str_fallback(self):
        out = normalize_health_issue({"random": "x"})
        # str(dict) — preserves the previous fallback behaviour
        assert "random" in out

    def test_non_string_non_dict_str_fallback(self):
        assert normalize_health_issue(42) == "42"


class TestNormalizeHealthAction:
    def test_string_passes_through(self):
        assert normalize_health_action("Water tomorrow") == "Water tomorrow"

    def test_dict_action_key(self):
        assert normalize_health_action({"action": "Flush"}) == "Flush"

    def test_dict_message_fallback(self):
        assert normalize_health_action({"message": "Check pH"}) == "Check pH"

    def test_dict_description_fallback(self):
        assert normalize_health_action({"description": "Top up"}) == "Top up"

    def test_dict_no_keys_str_fallback(self):
        out = normalize_health_action({"random": "x"})
        assert "random" in out


class TestNormalizeHealthHistoryHelpers:
    """History-listing variants do NOT add the [category] prefix —
    pin that difference."""

    def test_issue_no_category_prefix(self):
        out = normalize_health_history_issue({"message": "Yellowing", "category": "Nutrient"})
        # Category is silently ignored — different from normalize_health_issue
        assert "[" not in out
        assert out == "Yellowing"

    def test_issue_uses_message_or_issue(self):
        assert normalize_health_history_issue({"issue": "Light burn"}) == "Light burn"

    def test_action_uses_message_or_action(self):
        assert normalize_health_history_action({"action": "Flush"}) == "Flush"
        assert normalize_health_history_action({"message": "Check pH"}) == "Check pH"


class TestParseHealthCheckJson:
    def test_valid_json(self):
        raw = (
            '{"score": 85, '
            '"issues": [{"description": "Yellow tips", "category": "Nutrient"}], '
            '"actions": [{"action": "Flush"}]}'
        )
        score, issues, actions = parse_health_check_json(raw)
        assert score == 85
        assert issues == ["[Nutrient] Yellow tips"]
        assert actions == ["Flush"]

    def test_strips_fence(self):
        raw = '```json\n{"score": 90, "issues": [], "actions": []}\n```'
        score, issues, actions = parse_health_check_json(raw)
        assert score == 90
        assert issues == []
        assert actions == []

    def test_invalid_json_returns_empty(self):
        score, issues, actions = parse_health_check_json("not json")
        assert score is None
        assert issues == []
        assert actions == []

    def test_string_lists_pass_through(self):
        raw = '{"score": 70, "issues": ["Low water"], "actions": ["Top up tomorrow"]}'
        score, issues, actions = parse_health_check_json(raw)
        assert score == 70
        assert issues == ["Low water"]
        assert actions == ["Top up tomorrow"]


class TestHealthHistoryMaxLimit:
    def test_cap_is_50(self):
        # The history endpoint silently caps the caller's `limit` here —
        # if this changes, the API contract changes too.
        assert HEALTH_HISTORY_MAX_LIMIT == 50
