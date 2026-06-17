"""Unit tests for app.ai.service pure helpers."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.ai.service import parse_optional_uuid


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
