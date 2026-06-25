"""Unit tests for AI chat tool execution helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest

from app.ai.models import AgentAction
from app.ai.tools import CHAT_TOOLS, execute_tool
from app.integrations.service import WebhookSyncResult


async def _create_grow(session, *, tenant_id):
    from app.grows.models import GrowCycle, Tent

    tent = Tent(
        tenant_id=tenant_id,
        name="Test Tent",
    )
    session.add(tent)
    await session.flush()

    grow = GrowCycle(
        tenant_id=tenant_id,
        tent_id=tent.id,
        name="Test Grow",
        grow_type="dwc",
        stage="vegetative",
    )
    session.add(grow)
    await session.commit()
    await session.refresh(grow)
    return grow


async def _create_integration(session, *, tenant_id, integration_type: str):
    from app.integrations.models import IntegrationConfig

    cfg = IntegrationConfig(
        tenant_id=tenant_id,
        type=integration_type,
        name=f"{integration_type} test",
        config="{}",
        webhook_secret="test-secret",
        enabled=True,
        poll_interval_s=300,
    )
    session.add(cfg)
    await session.commit()
    await session.refresh(cfg)
    return cfg


class TestChatToolsSchema:
    def test_chat_tools_include_integration_trigger_sync(self):
        names = {tool["function"]["name"] for tool in CHAT_TOOLS}
        assert "integration_trigger_sync" in names


class TestExecuteToolIntegrationSync:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_integration_trigger_sync_requires_uuid(self, db_session, db_tenant):
        grow = await _create_grow(db_session, tenant_id=db_tenant["tenant"].id)

        out = await execute_tool(
            "integration_trigger_sync",
            {"integration_id": "not-a-uuid"},
            session=db_session,
            tenant_id=db_tenant["tenant"].id,
            grow_id=grow.id,
        )

        assert out == "Error: integration_id must be a valid UUID."

    @pytest.mark.asyncio(loop_scope="session")
    async def test_integration_trigger_sync_blocks_unsupported_connector(self, db_session, db_tenant):
        grow = await _create_grow(db_session, tenant_id=db_tenant["tenant"].id)
        cfg = await _create_integration(db_session, tenant_id=db_tenant["tenant"].id, integration_type="tuya")

        out = await execute_tool(
            "integration_trigger_sync",
            {"integration_id": str(cfg.id)},
            session=db_session,
            tenant_id=db_tenant["tenant"].id,
            grow_id=grow.id,
        )

        assert isinstance(out, dict)
        assert out["status"] == "blocked"
        assert out["phase"] == "blocked"
        assert out["error"] == "Unsupported integration connector: tuya"
        assert out["policy"]["integration_type"] == "tuya"

        action = await db_session.get(AgentAction, UUID(out["action_id"]))
        assert action is not None
        assert action.status == "blocked"
        assert action.action_type == "integration_trigger_sync"
        assert action.execution_json["error"] == "Unsupported integration connector: tuya"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_integration_trigger_sync_runs_when_allowed(self, db_session, db_tenant):
        grow = await _create_grow(db_session, tenant_id=db_tenant["tenant"].id)
        cfg = await _create_integration(db_session, tenant_id=db_tenant["tenant"].id, integration_type="pulse")

        with patch("app.integrations.service.trigger_sync", new_callable=AsyncMock) as mock_trigger_sync:
            mock_trigger_sync.return_value = WebhookSyncResult(
                status="success",
                readings_count=3,
                error_message=None,
            )

            out = await execute_tool(
                "integration_trigger_sync",
                {"integration_id": str(cfg.id)},
                session=db_session,
                tenant_id=db_tenant["tenant"].id,
                grow_id=grow.id,
            )

        mock_trigger_sync.assert_awaited_once()
        assert out == "Integration sync completed: status=success, readings=3"
