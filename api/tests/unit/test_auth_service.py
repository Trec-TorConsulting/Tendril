"""Unit tests for app.auth.service pure helpers + cookie configuration.

⚠️ Security-sensitive — every cookie attribute and every validator
behaviour here is load-bearing. If a test fails, the production cookie
flags are wrong and an attacker may be able to exfiltrate tokens.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import bcrypt
import pytest
from fastapi import Response

from app.auth.service import (
    ACCESS_COOKIE_MAX_AGE_S,
    CSRF_COOKIE_MAX_AGE_S,
    REFRESH_COOKIE_MAX_AGE_S,
    VALID_LAYOUT_MODES,
    VALID_PREFERENCE_KEYS,
    clear_auth_cookies,
    cookie_domain,
    hash_password,
    is_secure,
    make_tenant_slug,
    merge_preferences,
    set_auth_cookies,
    validate_layout_mode,
    validate_preference_keys,
    verify_password,
)

# ─── Password ─────────────────────────────────────────────────────────────────


class TestHashAndVerifyPassword:
    def test_hash_produces_bcrypt(self):
        h = hash_password("Corr3ctHorse!9")
        assert bcrypt.checkpw(b"Corr3ctHorse!9", h.encode())

    def test_verify_rejects_wrong(self):
        h = hash_password("right-password")
        assert verify_password("right-password", h) is True
        assert verify_password("wrong-password", h) is False

    def test_hashes_are_unique(self):
        # Different salts → different hashes for the same password
        assert hash_password("same") != hash_password("same")


# ─── Slug ─────────────────────────────────────────────────────────────────────


class TestMakeTenantSlug:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Acme Co", "acme-co"),
            ("Über Greenhouse", "ber-greenhouse"),  # non-[a-z0-9] → hyphen
            ("---weird-name---", "weird-name"),
            ("UPPER_CASE Name", "upper-case-name"),
            ("a" * 200, "a" * 100),  # truncates to 100
            ("", ""),
        ],
    )
    def test_cases(self, name, expected):
        assert make_tenant_slug(name) == expected


# ─── Cookie environment helpers ───────────────────────────────────────────────


class TestIsSecure:
    @patch.dict(os.environ, {"DOMAIN": ""}, clear=False)
    def test_empty_domain_is_local(self):
        assert is_secure() is False

    @patch.dict(os.environ, {"DOMAIN": "localhost"}, clear=False)
    def test_localhost_is_local(self):
        assert is_secure() is False

    @patch.dict(os.environ, {"DOMAIN": "tendrilgrow.com"}, clear=False)
    def test_real_domain_is_secure(self):
        assert is_secure() is True


class TestCookieDomain:
    @patch.dict(os.environ, {"DOMAIN": ""}, clear=False)
    def test_empty_returns_none(self):
        assert cookie_domain() is None

    @patch.dict(os.environ, {"DOMAIN": "localhost"}, clear=False)
    def test_localhost_returns_none(self):
        assert cookie_domain() is None

    @patch.dict(os.environ, {"DOMAIN": "tendrilgrow.com"}, clear=False)
    def test_two_part_domain(self):
        assert cookie_domain() == ".tendrilgrow.com"

    @patch.dict(os.environ, {"DOMAIN": "api.tendrilgrow.com"}, clear=False)
    def test_three_part_anchors_to_parent(self):
        # Cross-subdomain sharing — api.* and app.* both use the same cookie.
        assert cookie_domain() == ".tendrilgrow.com"

    @patch.dict(os.environ, {"DOMAIN": "deep.api.tendrilgrow.com"}, clear=False)
    def test_deep_subdomain_still_anchors_to_apex(self):
        assert cookie_domain() == ".tendrilgrow.com"


# ─── Cookie issuance ──────────────────────────────────────────────────────────


class TestCookieLifetimes:
    """Pin the lifetimes — frontend session UX assumes these."""

    def test_access_is_15_minutes(self):
        assert ACCESS_COOKIE_MAX_AGE_S == 15 * 60

    def test_refresh_is_7_days(self):
        assert REFRESH_COOKIE_MAX_AGE_S == 7 * 24 * 60 * 60

    def test_csrf_matches_refresh(self):
        # CSRF cookie has to outlive any pending session; if it expires
        # before refresh, the user gets locked out of POSTs.
        assert CSRF_COOKIE_MAX_AGE_S == REFRESH_COOKIE_MAX_AGE_S


@patch.dict(os.environ, {"DOMAIN": "tendrilgrow.com"}, clear=False)
class TestSetAuthCookies:
    def test_emits_all_three_cookies(self):
        resp = Response()
        csrf = set_auth_cookies(resp, "access-tok", "refresh-tok")
        header = resp.headers.getlist("set-cookie")
        # Three Set-Cookie headers
        joined = " | ".join(header)
        assert "access_token=access-tok" in joined
        assert "refresh_token=refresh-tok" in joined
        assert f"csrf_token={csrf}" in joined

    def test_access_cookie_is_http_only(self):
        resp = Response()
        set_auth_cookies(resp, "a", "r")
        # The access cookie must be httponly to keep tokens out of JS
        access_line = next(h for h in resp.headers.getlist("set-cookie") if h.startswith("access_token="))
        assert "HttpOnly" in access_line

    def test_refresh_cookie_path_is_scoped_to_auth(self):
        resp = Response()
        set_auth_cookies(resp, "a", "r")
        refresh_line = next(h for h in resp.headers.getlist("set-cookie") if h.startswith("refresh_token="))
        assert "Path=/v1/auth" in refresh_line  # narrower than /
        assert "HttpOnly" in refresh_line

    def test_csrf_cookie_is_not_http_only(self):
        # Double-submit pattern requires JS to read this cookie.
        resp = Response()
        set_auth_cookies(resp, "a", "r")
        csrf_line = next(h for h in resp.headers.getlist("set-cookie") if h.startswith("csrf_token="))
        assert "HttpOnly" not in csrf_line

    def test_emits_csrf_response_header(self):
        resp = Response()
        csrf = set_auth_cookies(resp, "a", "r")
        assert resp.headers.get("X-CSRF-Token") == csrf

    def test_returns_fresh_csrf_each_call(self):
        resp1 = Response()
        resp2 = Response()
        assert set_auth_cookies(resp1, "a", "r") != set_auth_cookies(resp2, "a", "r")


@patch.dict(os.environ, {"DOMAIN": ""}, clear=False)
class TestSetAuthCookiesLocalDev:
    def test_no_secure_flag_in_local_dev(self):
        resp = Response()
        set_auth_cookies(resp, "a", "r")
        headers = " | ".join(resp.headers.getlist("set-cookie"))
        # No "Secure" attribute when DOMAIN is empty (HTTP local dev).
        assert "Secure" not in headers


class TestClearAuthCookies:
    @patch.dict(os.environ, {"DOMAIN": ""}, clear=False)
    def test_clears_all_three(self):
        resp = Response()
        clear_auth_cookies(resp)
        headers = " | ".join(resp.headers.getlist("set-cookie"))
        # delete_cookie emits a Set-Cookie with Max-Age=0 (or empty
        # value) for each key.  We assert by-name presence.
        assert "access_token=" in headers
        assert "refresh_token=" in headers
        assert "csrf_token=" in headers


# ─── Preferences validation ───────────────────────────────────────────────────


class TestValidateLayoutMode:
    @pytest.mark.parametrize("mode", sorted(VALID_LAYOUT_MODES))
    def test_accepts_each_valid_mode(self, mode):
        validate_layout_mode(mode)  # no raise

    def test_rejects_unknown(self):
        with pytest.raises(ValueError, match="Invalid layout_mode"):
            validate_layout_mode("blueprint")

    def test_layout_modes_canonical_set(self):
        # Frontend hard-codes this list in the settings page.
        assert frozenset({"beginner", "home", "standard", "pro", "commercial"}) == VALID_LAYOUT_MODES


class TestValidatePreferenceKeys:
    def test_accepts_empty(self):
        validate_preference_keys({})

    def test_accepts_subset(self):
        validate_preference_keys({"temp_unit": "F", "theme": "dark"})

    def test_rejects_unknown(self):
        with pytest.raises(ValueError, match="Invalid preference keys"):
            validate_preference_keys({"temp_unit": "F", "rogue_key": "x"})

    def test_valid_keys_canonical_set(self):
        # Adding a new preference requires touching this set — guard against drift.
        assert "temp_unit" in VALID_PREFERENCE_KEYS
        assert "show_onboarding" in VALID_PREFERENCE_KEYS


class TestMergePreferences:
    def test_none_current_treated_as_empty(self):
        out = merge_preferences(None, {"temp_unit": "F"})
        assert out == {"temp_unit": "F"}

    def test_overlay_preserves_unspecified(self):
        out = merge_preferences({"theme": "dark", "temp_unit": "C"}, {"temp_unit": "F"})
        assert out == {"theme": "dark", "temp_unit": "F"}

    def test_none_value_removes_key(self):
        # User reset semantics: setting a key to None deletes it.
        out = merge_preferences({"theme": "dark", "temp_unit": "C"}, {"temp_unit": None})
        assert "temp_unit" not in out
        assert out == {"theme": "dark"}

    def test_none_value_can_remove_existing_only(self):
        # An update of {key: None} where key isn't present is a no-op.
        out = merge_preferences({"theme": "dark"}, {"nonexistent": None})
        assert out == {"theme": "dark"}
