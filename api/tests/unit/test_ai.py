"""Integration tests for Phase 4 AI endpoints — health check, coach tip, insights, report."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.ai.models import AgentAction
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


@pytest_asyncio.fixture
async def grow_with_data(client, tenant):
    """Create a tent, grow, and bucket for AI tests."""
    tent = await client.post(
        "/v1/tents",
        json={"name": "AI Tent", "environment_type": "indoor"},
        headers=tenant["headers"],
    )
    tent_id = tent.json()["id"]

    grow = await client.post(
        "/v1/grows",
        json={"name": "AI Grow", "tent_id": tent_id, "grow_type": "dwc"},
        headers=tenant["headers"],
    )
    grow_id = grow.json()["id"]

    bucket = await client.post(
        "/v1/buckets",
        json={"grow_cycle_id": grow_id, "position": 1, "label": "B1"},
        headers=tenant["headers"],
    )
    bucket_id = bucket.json()["id"]

    # Add sensor reading
    await client.post(
        "/v1/sensors",
        json={"bucket_id": bucket_id, "ph": 6.2, "ec": 1.4, "water_temp_f": 20.5},
        headers=tenant["headers"],
    )

    return {"tenant": tenant, "tent_id": tent_id, "grow_id": grow_id, "bucket_id": bucket_id}


class TestHealthCheck:
    @patch("app.ai.gemini.is_configured", return_value=True)
    @patch("app.ai.gemini.chat_completion", new_callable=AsyncMock)
    async def test_health_check_success(self, mock_ai, mock_configured, client, grow_with_data, db_session):
        mock_ai.return_value = '{"score": 85, "issues": ["Slight pH drift"], "actions": ["Adjust pH down"]}'

        resp = await client.post(
            "/v1/ai/health-check",
            json={
                "grow_id": grow_with_data["grow_id"],
                "observations": {"root_health": "white and healthy"},
            },
            headers=grow_with_data["tenant"]["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 85
        assert len(data["issues"]) >= 1
        assert len(data["actions"]) >= 1

        action_rows = (
            await db_session.execute(
                select(AgentAction)
                .where(AgentAction.grow_cycle_id == grow_with_data["grow_id"])
                .order_by(AgentAction.created_at)
            )
        ).scalars().all()
        assert len(action_rows) == 1
        assert action_rows[0].source == "health_check"
        assert action_rows[0].action_type == "create_task"
        assert action_rows[0].auto_approved is True
        assert action_rows[0].status == "verified"
        assert action_rows[0].metadata_json["safe_action"] is True

    @patch("app.ai.gemini.is_configured", return_value=True)
    @patch("app.ai.gemini.chat_completion", new_callable=AsyncMock)
    async def test_health_check_mixed_safe_and_pending_approval_actions(
        self,
        mock_ai,
        mock_configured,
        client,
        grow_with_data,
        db_session,
    ):
        mock_ai.return_value = (
            '{"score": 70, "issues": ["High humidity"], '
            '"actions": ["Adjust pH down", "Turn on exhaust fan now"]}'
        )

        resp = await client.post(
            "/v1/ai/health-check",
            json={
                "grow_id": grow_with_data["grow_id"],
                "observations": {"canopy": "humid"},
            },
            headers=grow_with_data["tenant"]["headers"],
        )
        assert resp.status_code == 200

        action_rows = (
            await db_session.execute(
                select(AgentAction)
                .where(AgentAction.grow_cycle_id == grow_with_data["grow_id"])
                .order_by(AgentAction.created_at)
            )
        ).scalars().all()
        assert len(action_rows) == 2

        safe_action = next(item for item in action_rows if item.action_type == "create_task")
        pending_action = next(item for item in action_rows if item.action_type == "control_equipment")

        assert safe_action.status == "verified"
        assert safe_action.auto_approved is True
        assert safe_action.metadata_json["safe_action"] is True

        assert pending_action.status == "pending_approval"
        assert pending_action.requires_approval is True
        assert pending_action.auto_approved is False
        assert pending_action.metadata_json["safe_action"] is False

    async def test_health_check_invalid_grow(self, client, tenant):
        resp = await client.post(
            "/v1/ai/health-check",
            json={
                "grow_id": "00000000-0000-0000-0000-000000000000",
                "observations": {},
            },
            headers=tenant["headers"],
        )
        # 404 if grow not found, or 503 if AI service not configured (checked first)
        assert resp.status_code in (404, 503)

    async def test_health_check_no_auth(self, client):
        resp = await client.post(
            "/v1/ai/health-check",
            json={"grow_id": "00000000-0000-0000-0000-000000000000", "observations": {}},
        )
        assert resp.status_code in (401, 403)


class TestCoachTip:
    @patch("app.ai.routes.chat_completion", new_callable=AsyncMock)
    async def test_coach_tip_success(self, mock_ai, client, grow_with_data):
        mock_ai.return_value = "Check your reservoir water level daily."

        resp = await client.post(
            "/v1/ai/coach-tip",
            json={"grow_id": grow_with_data["grow_id"]},
            headers=grow_with_data["tenant"]["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "tip" in data
        assert len(data["tip"]) > 0


class TestInsights:
    @patch("app.ai.routes.chat_completion", new_callable=AsyncMock)
    async def test_harvest_predict(self, mock_ai, client, grow_with_data):
        mock_ai.return_value = '{"estimated_days": 45, "confidence": "medium"}'

        resp = await client.post(
            "/v1/ai/insights",
            json={
                "grow_id": grow_with_data["grow_id"],
                "insight_type": "harvest_predict",
            },
            headers=grow_with_data["tenant"]["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["insight_type"] == "harvest_predict"

    async def test_invalid_insight_type(self, client, grow_with_data):
        resp = await client.post(
            "/v1/ai/insights",
            json={
                "grow_id": grow_with_data["grow_id"],
                "insight_type": "invalid_type",
            },
            headers=grow_with_data["tenant"]["headers"],
        )
        assert resp.status_code in (400, 422)


class TestGrowReport:
    async def test_report_not_found(self, client, tenant):
        resp = await client.get(
            "/v1/ai/report/00000000-0000-0000-0000-000000000000",
            headers=tenant["headers"],
        )
        assert resp.status_code == 404

    async def test_report_success(self, client, grow_with_data):
        resp = await client.get(
            f"/v1/ai/report/{grow_with_data['grow_id']}",
            headers=grow_with_data["tenant"]["headers"],
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF")

    async def test_report_no_auth(self, client, grow_with_data):
        resp = await client.get(f"/v1/ai/report/{grow_with_data['grow_id']}")
        assert resp.status_code in (401, 403)
