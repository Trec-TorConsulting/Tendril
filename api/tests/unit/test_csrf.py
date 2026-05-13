"""CSRF middleware tests — valid token, missing token, invalid token, cookie-based auth flags."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.middleware.csrf import generate_csrf_token

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def raw_client(_setup_db):
    """Client without pre-set CSRF cookie (for testing missing/invalid scenarios)."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------- CSRF Token Validation ----------


class TestCSRFValidToken:
    async def test_post_with_valid_csrf_succeeds(self, raw_client):
        """POST request with matching CSRF cookie + header passes CSRF check."""
        # Use a fresh client so we control the exact cookie state
        raw_client.cookies.set("csrf_token", "my-csrf-token")
        # Logout endpoint requires no auth but IS subject to CSRF middleware
        resp = await raw_client.post(
            "/v1/auth/logout",
            headers={"X-CSRF-Token": "my-csrf-token"},
        )
        # 200 means CSRF passed and endpoint executed successfully
        assert resp.status_code == 200

    async def test_get_does_not_require_csrf(self, client):
        """GET requests do not require CSRF tokens."""
        resp = await client.post(
            "/v1/auth/register",
            json={
                "email": "csrf-get@example.com",
                "password": "SecurePass123!",
                "display_name": "Get User",
                "tenant_name": "Get Org",
            },
        )
        token = resp.json()["access_token"]

        resp = await client.get("/v1/tents", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200


class TestCSRFMissingToken:
    async def test_post_without_csrf_header_rejected(self, raw_client):
        """POST without X-CSRF-Token header is rejected with 403."""
        resp = await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "csrf-no-header@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        token = resp.json()["access_token"]

        # Set a CSRF cookie but don't send the header
        raw_client.cookies.set("csrf_token", "some-csrf-value")
        resp = await raw_client.post(
            "/v1/tents",
            json={"name": "Should Fail"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert "CSRF" in resp.json()["detail"]

    async def test_post_without_csrf_cookie_rejected(self, raw_client):
        """POST without csrf_token cookie is rejected with 403."""
        resp = await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "csrf-no-cookie@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        token = resp.json()["access_token"]

        # Send header but no cookie
        resp = await raw_client.post(
            "/v1/tents",
            json={"name": "Should Fail"},
            headers={"Authorization": f"Bearer {token}", "X-CSRF-Token": "some-value"},
        )
        assert resp.status_code == 403
        assert "CSRF" in resp.json()["detail"]


class TestCSRFInvalidToken:
    async def test_mismatched_csrf_tokens_rejected(self, raw_client):
        """POST where header != cookie CSRF value is rejected."""
        resp = await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "csrf-mismatch@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        token = resp.json()["access_token"]

        # Set cookie to one value, header to another
        raw_client.cookies.set("csrf_token", "cookie-value-abc")
        resp = await raw_client.post(
            "/v1/tents",
            json={"name": "Should Fail"},
            headers={"Authorization": f"Bearer {token}", "X-CSRF-Token": "header-value-xyz"},
        )
        assert resp.status_code == 403
        assert "CSRF token mismatch" in resp.json()["detail"]


class TestCSRFExemptPaths:
    async def test_login_exempt_from_csrf(self, raw_client):
        """Login endpoint does not require CSRF tokens."""
        await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "csrf-exempt@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        # Login without any CSRF token — should still work
        resp = await raw_client.post(
            "/v1/auth/login",
            json={
                "email": "csrf-exempt@example.com",
                "password": "SecurePass123!",
            },
        )
        assert resp.status_code == 200

    async def test_register_exempt_from_csrf(self, raw_client):
        """Register endpoint does not require CSRF tokens."""
        resp = await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "csrf-exempt2@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        assert resp.status_code == 201

    async def test_refresh_exempt_from_csrf(self, raw_client):
        """Refresh endpoint does not require CSRF tokens."""
        reg = await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "csrf-exempt3@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        refresh_token = reg.json()["refresh_token"]

        resp = await raw_client.post(
            "/v1/auth/refresh",
            json={
                "refresh_token": refresh_token,
            },
        )
        assert resp.status_code == 200


# ---------- Cookie-Based Auth (httpOnly, Secure, SameSite) ----------


class TestCookieAuthFlags:
    async def test_login_sets_httponly_access_token(self, raw_client):
        """Login response sets access_token cookie with httpOnly flag."""
        await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "cookie-flags@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        resp = await raw_client.post(
            "/v1/auth/login",
            json={
                "email": "cookie-flags@example.com",
                "password": "SecurePass123!",
            },
        )
        assert resp.status_code == 200

        # Check Set-Cookie headers
        cookies = resp.headers.get_list("set-cookie")
        access_cookie = next((c for c in cookies if c.startswith("access_token=")), None)
        assert access_cookie is not None, "access_token cookie not set"
        assert "httponly" in access_cookie.lower(), "access_token must be httpOnly"
        assert "samesite=lax" in access_cookie.lower(), "access_token must be SameSite=lax"

    async def test_login_sets_httponly_refresh_token(self, raw_client):
        """Login response sets refresh_token cookie with httpOnly flag."""
        await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "cookie-refresh@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        resp = await raw_client.post(
            "/v1/auth/login",
            json={
                "email": "cookie-refresh@example.com",
                "password": "SecurePass123!",
            },
        )
        cookies = resp.headers.get_list("set-cookie")
        refresh_cookie = next((c for c in cookies if c.startswith("refresh_token=")), None)
        assert refresh_cookie is not None, "refresh_token cookie not set"
        assert "httponly" in refresh_cookie.lower(), "refresh_token must be httpOnly"
        assert "samesite=lax" in refresh_cookie.lower()
        assert "/v1/auth" in refresh_cookie, "refresh_token path should be /v1/auth"

    async def test_login_sets_csrf_cookie_not_httponly(self, raw_client):
        """Login response sets csrf_token cookie that is NOT httpOnly (JS-readable)."""
        await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "cookie-csrf@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        resp = await raw_client.post(
            "/v1/auth/login",
            json={
                "email": "cookie-csrf@example.com",
                "password": "SecurePass123!",
            },
        )
        cookies = resp.headers.get_list("set-cookie")
        csrf_cookie = next((c for c in cookies if c.startswith("csrf_token=")), None)
        assert csrf_cookie is not None, "csrf_token cookie not set"
        # CSRF cookie must NOT be httpOnly so JavaScript can read it
        assert "httponly" not in csrf_cookie.lower(), "csrf_token must NOT be httpOnly"

    async def test_login_returns_csrf_header(self, raw_client):
        """Login response includes X-CSRF-Token header for client convenience."""
        await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "cookie-header@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        resp = await raw_client.post(
            "/v1/auth/login",
            json={
                "email": "cookie-header@example.com",
                "password": "SecurePass123!",
            },
        )
        assert "x-csrf-token" in resp.headers
        assert len(resp.headers["x-csrf-token"]) > 20  # Should be a real token

    async def test_register_sets_auth_cookies(self, raw_client):
        """Register also sets the same auth cookies as login."""
        resp = await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "cookie-register@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        assert resp.status_code == 201
        cookies = resp.headers.get_list("set-cookie")
        cookie_names = [c.split("=")[0] for c in cookies]
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names
        assert "csrf_token" in cookie_names


# ---------- XSS Token Access Verification ----------


class TestXSSProtection:
    async def test_access_token_not_accessible_via_js(self, raw_client):
        """Verify access_token has httpOnly so document.cookie cannot read it.

        This is a server-side verification that the flag is set correctly.
        Actual XSS testing requires a browser, but we verify the flag is present.
        """
        await raw_client.post(
            "/v1/auth/register",
            json={
                "email": "xss-test@example.com",
                "password": "SecurePass123!",
                "display_name": "User",
                "tenant_name": "Org",
            },
        )
        resp = await raw_client.post(
            "/v1/auth/login",
            json={
                "email": "xss-test@example.com",
                "password": "SecurePass123!",
            },
        )
        cookies = resp.headers.get_list("set-cookie")

        for cookie in cookies:
            name = cookie.split("=")[0]
            if name in ("access_token", "refresh_token"):
                assert "httponly" in cookie.lower(), (
                    f"{name} MUST be httpOnly to prevent XSS access via document.cookie"
                )
            elif name == "csrf_token":
                # CSRF token is intentionally readable by JS
                assert "httponly" not in cookie.lower()

    def test_csrf_token_generation_is_cryptographic(self):
        """CSRF tokens use cryptographically secure random generation."""
        tokens = {generate_csrf_token() for _ in range(100)}
        # All should be unique (collision probability ~0 with 32-byte random)
        assert len(tokens) == 100
        # Tokens should be reasonable length
        assert all(len(t) >= 32 for t in tokens)
