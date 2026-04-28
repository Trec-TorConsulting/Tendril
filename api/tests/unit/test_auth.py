"""Auth tests — registration, login, token refresh, RBAC."""
from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_register(client: AsyncClient):
    resp = await client.post("/v1/auth/register", json={
        "email": "new@example.com",
        "password": "SecurePass123!",
        "display_name": "New User",
        "tenant_name": "My Grow Op",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "dupe@example.com",
        "password": "SecurePass123!",
        "display_name": "User",
        "tenant_name": "Org",
    }
    await client.post("/v1/auth/register", json=payload)
    resp = await client.post("/v1/auth/register", json=payload)
    assert resp.status_code == 409


async def test_login(client: AsyncClient):
    # Register first
    await client.post("/v1/auth/register", json={
        "email": "login@example.com",
        "password": "SecurePass123!",
        "display_name": "Login User",
        "tenant_name": "Login Org",
    })
    # Login
    resp = await client.post("/v1/auth/login", json={
        "email": "login@example.com",
        "password": "SecurePass123!",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "SecurePass123!",
        "display_name": "User",
        "tenant_name": "Org",
    })
    resp = await client.post("/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401


async def test_refresh_token(client: AsyncClient):
    reg = await client.post("/v1/auth/register", json={
        "email": "refresh@example.com",
        "password": "SecurePass123!",
        "display_name": "User",
        "tenant_name": "Org",
    })
    refresh_token = reg.json()["refresh_token"]

    resp = await client.post("/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/v1/auth/me")
    assert resp.status_code == 401  # No bearer token


async def test_me_authenticated(client: AsyncClient):
    reg = await client.post("/v1/auth/register", json={
        "email": "me@example.com",
        "password": "SecurePass123!",
        "display_name": "Me User",
        "tenant_name": "Me Org",
    })
    token = reg.json()["access_token"]
    resp = await client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "owner"
