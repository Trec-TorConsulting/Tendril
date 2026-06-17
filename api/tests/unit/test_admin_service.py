"""Unit tests for app.admin.service pure helpers + custom errors."""

from __future__ import annotations

import pytest

from app.admin.service import (
    InvalidPlatformRoleError,
    SelfDeleteError,
    SelfDemotionError,
    TenantSlugTakenError,
    coerce_platform_role,
)
from app.tenants.models import PlatformRole


class TestCoercePlatformRole:
    @pytest.mark.parametrize("value", [r.value for r in PlatformRole])
    def test_accepts_every_enum_value(self, value):
        # Round-trip: enum.value -> PlatformRole equality
        assert coerce_platform_role(value).value == value

    def test_rejects_unknown(self):
        with pytest.raises(InvalidPlatformRoleError) as exc:
            coerce_platform_role("god-mode")
        assert exc.value.value == "god-mode"

    def test_rejects_empty(self):
        with pytest.raises(InvalidPlatformRoleError):
            coerce_platform_role("")

    def test_super_admin_round_trip(self):
        # The frontend posts the exact string "super_admin"; lock this in.
        assert coerce_platform_role("super_admin") == PlatformRole.super_admin


class TestCustomErrors:
    """The route layer maps each of these to a specific HTTP status —
    pin both that they carry the attributes the routes inspect and that
    their string form matches the user-visible message."""

    def test_tenant_slug_taken_carries_slug(self):
        err = TenantSlugTakenError("my-org")
        assert err.slug == "my-org"
        assert "my-org" in str(err)

    def test_invalid_platform_role_carries_value(self):
        err = InvalidPlatformRoleError("blue-admin")
        assert err.value == "blue-admin"
        assert "blue-admin" in str(err)

    def test_self_demotion_error_message(self):
        err = SelfDemotionError("Cannot remove your own admin access")
        assert "admin access" in str(err)

    def test_self_delete_error_message(self):
        err = SelfDeleteError("Cannot delete yourself")
        assert "delete yourself" in str(err)

    def test_self_demotion_is_exception(self):
        assert issubclass(SelfDemotionError, Exception)

    def test_self_delete_is_exception(self):
        assert issubclass(SelfDeleteError, Exception)
