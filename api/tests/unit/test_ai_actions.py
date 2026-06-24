from __future__ import annotations

from uuid import uuid4

import bcrypt
import pytest
import pytest_asyncio
from sqlalchemy import select

from app.ai import service
from app.ai.models import AgentActionApproval
from app.auth.jwt import create_access_token
from app.tenants.models import PlatformRole, TenantMembership, TenantRole, User
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


@pytest_asyncio.fixture
async def pending_action(db_session, tenant):
    action = await service.create_agent_action(
        db_session,
        tenant_id=tenant["tenant"].id,
        source="health_check",
        action_type="update_journal",
        title="Add a follow-up journal note",
        idempotency_key=service.build_agent_action_idempotency_key(
            tenant_id=tenant["tenant"].id,
            source="health_check",
            action_type="update_journal",
            grow_cycle_id=None,
            conversation_id=None,
            dedupe_token="pending-approval",
        ),
        created_by_user_id=tenant["user"].id,
        requires_approval=True,
        auto_approved=False,
    )
    await service.transition_agent_action(
        db_session,
        action,
        next_status=service.AGENT_ACTION_STATUS_PENDING_APPROVAL,
    )
    approval = await service.create_agent_action_approval(
        db_session,
        tenant_id=tenant["tenant"].id,
        action_id=action.id,
        requested_by_user_id=tenant["user"].id,
    )
    return {"action": action, "approval": approval}


async def _create_viewer_headers(db_session, tenant):
    user = User(
        email=f"viewer-{uuid4().hex[:8]}@test.com",
        password_hash=bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode(),
        display_name="Viewer User",
        platform_role=PlatformRole.user,
    )
    db_session.add(user)
    await db_session.flush()
    db_session.add(TenantMembership(tenant_id=tenant["tenant"].id, user_id=user.id, role=TenantRole.viewer))
    await db_session.commit()

    token = create_access_token(
        user.id,
        platform_role=user.platform_role.value,
        tenant_id=tenant["tenant"].id,
        tenant_role=TenantRole.viewer.value,
        account_id=tenant["account"].id,
    )
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": "test-csrf-token",
    }


class TestAiActionRoutes:
    async def test_list_actions_returns_pending_action(self, client, tenant, pending_action):
        resp = await client.get("/v1/ai/actions", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == str(pending_action["action"].id)
        assert data["items"][0]["status"] == service.AGENT_ACTION_STATUS_PENDING_APPROVAL
        assert data["items"][0]["pending_approval"]["id"] == str(pending_action["approval"].id)
        assert data["items"][0]["proposal"]["headline"] == "Add a follow-up journal note"
        assert data["items"][0]["proposal"]["approval"]["status"] == service.AGENT_APPROVAL_STATUS_PENDING
        assert data["items"][0]["proposal"]["surface"] == "ai_side_panel"
        assert data["items"][0]["proposal"]["steps"][2]["status"] == "current"

    async def test_get_action_returns_approvals(self, client, tenant, pending_action):
        resp = await client.get(f"/v1/ai/actions/{pending_action['action'].id}", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(pending_action["action"].id)
        assert len(data["approvals"]) == 1
        assert data["approvals"][0]["status"] == service.AGENT_APPROVAL_STATUS_PENDING
        assert data["pending_approval"]["reason"] is None
        assert data["proposal"]["approval"]["required"] is True
        assert data["proposal"]["steps"][3]["status"] == "pending"

    async def test_approve_action_updates_action_and_approval(self, client, tenant, pending_action, db_session):
        resp = await client.post(
            f"/v1/ai/actions/{pending_action['action'].id}/approve",
            json={"reason": "Looks safe"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == service.AGENT_ACTION_STATUS_APPROVED
        assert data["approvals"][0]["status"] == service.AGENT_APPROVAL_STATUS_APPROVED
        assert data["approvals"][0]["reason"] == "Looks safe"
        assert data["pending_approval"] is None
        assert data["proposal"]["approval"]["status"] == service.AGENT_APPROVAL_STATUS_APPROVED
        assert data["proposal"]["steps"][2]["status"] == "completed"

        await db_session.refresh(pending_action["approval"])
        refreshed = (
            await db_session.execute(
                select(AgentActionApproval).where(AgentActionApproval.id == pending_action["approval"].id)
            )
        ).scalar_one()
        assert refreshed.reviewed_by_user_id == tenant["user"].id

    async def test_reject_action_updates_action_and_approval(self, client, tenant, pending_action):
        resp = await client.post(
            f"/v1/ai/actions/{pending_action['action'].id}/reject",
            json={"reason": "Needs review"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == service.AGENT_ACTION_STATUS_REJECTED
        assert data["approvals"][0]["status"] == service.AGENT_APPROVAL_STATUS_REJECTED

    async def test_viewer_cannot_approve_action(self, client, tenant, pending_action, db_session):
        viewer_headers = await _create_viewer_headers(db_session, tenant)
        resp = await client.post(
            f"/v1/ai/actions/{pending_action['action'].id}/approve",
            json={"reason": "nope"},
            headers=viewer_headers,
        )
        assert resp.status_code == 403

    async def test_cannot_approve_action_without_pending_approval(self, client, tenant, db_session):
        action = await service.create_agent_action(
            db_session,
            tenant_id=tenant["tenant"].id,
            source="health_check",
            action_type="create_task",
            title="Already safe",
            idempotency_key=service.build_agent_action_idempotency_key(
                tenant_id=tenant["tenant"].id,
                source="health_check",
                action_type="create_task",
                grow_cycle_id=None,
                conversation_id=None,
                dedupe_token="no-approval",
            ),
            created_by_user_id=tenant["user"].id,
            requires_approval=False,
            auto_approved=True,
        )

        resp = await client.post(
            f"/v1/ai/actions/{action.id}/approve",
            json={"reason": "no pending approval"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 409
        assert "no pending approval" in resp.json()["detail"].lower()
