"""Unit tests for app.ai.service pure helpers."""

from __future__ import annotations

import base64
from uuid import UUID, uuid4

import pytest

from app.ai.service import (
    DEFAULT_DIAGNOSIS_OVERALL_SCORE,
    DEFAULT_DIAGNOSIS_OVERALL_SEVERITY,
    DIAGNOSIS_SYSTEM_PROMPT,
    MAX_DIAGNOSE_IMAGE_BYTES,
    DiagnoseImageError,
    build_diagnosis_prompt,
    decode_diagnose_image,
    parse_diagnosis_response,
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
