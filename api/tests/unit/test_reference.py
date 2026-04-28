"""Integration tests for reference data API — strains and nutrients."""

from __future__ import annotations

import pytest
import pytest_asyncio
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


class TestReferenceStrains:
    async def test_search_strains(self, client, tenant):
        resp = await client.get("/v1/reference/strains?q=blue", headers=tenant["headers"])
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_search_strains_requires_min_query(self, client, tenant):
        resp = await client.get("/v1/reference/strains?q=a", headers=tenant["headers"])
        assert resp.status_code == 422  # min 2 chars

    async def test_search_strains_with_limit(self, client, tenant):
        resp = await client.get("/v1/reference/strains?q=og&limit=5", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()) <= 5

    async def test_search_strains_requires_auth(self, client):
        resp = await client.get("/v1/reference/strains?q=blue")
        assert resp.status_code in (401, 403)


class TestReferenceNutrients:
    async def test_search_nutrients(self, client, tenant):
        resp = await client.get("/v1/reference/nutrients?q=flora", headers=tenant["headers"])
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_search_nutrients_requires_min_query(self, client, tenant):
        resp = await client.get("/v1/reference/nutrients?q=a", headers=tenant["headers"])
        assert resp.status_code == 422

    async def test_nutrient_barcode_lookup(self, client, tenant):
        resp = await client.get("/v1/reference/nutrients/barcode/000000000000", headers=tenant["headers"])
        # Will return 200 with data or 404 if barcode not in reference DB
        assert resp.status_code in (200, 404)

    async def test_nutrients_requires_auth(self, client):
        resp = await client.get("/v1/reference/nutrients?q=flora")
        assert resp.status_code in (401, 403)
