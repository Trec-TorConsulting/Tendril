"""Integration tests for Phase 5 — notifications, billing, data export."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.notifications.models import NotificationChannel, NotificationLog, NotificationPreference
from app.notifications.service import dispatch_alert
from tests.conftest import TenantFactory

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture
async def tenant(db_session):
    factory = TenantFactory(db_session)
    return await factory.create()


# ---------- Notification Channels ----------


class TestNotificationChannels:
    async def test_create_discord_channel(self, client, tenant):
        resp = await client.post(
            "/v1/notifications/channels",
            json={
                "channel_type": "discord",
                "name": "Dev Alerts",
                "config": {"webhook_url": "https://discord.com/api/webhooks/test"},
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["channel_type"] == "discord"
        assert data["name"] == "Dev Alerts"
        assert data["enabled"] is True

    async def test_list_channels(self, client, tenant):
        await client.post(
            "/v1/notifications/channels",
            json={"channel_type": "slack", "name": "Slack", "config": {"webhook_url": "https://hooks.slack.com/test"}},
            headers=tenant["headers"],
        )
        resp = await client.get("/v1/notifications/channels", headers=tenant["headers"])
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 1

    async def test_update_channel(self, client, tenant):
        create = await client.post(
            "/v1/notifications/channels",
            json={"channel_type": "email", "name": "Old", "config": {"email": "a@b.com"}},
            headers=tenant["headers"],
        )
        ch_id = create.json()["id"]

        resp = await client.patch(
            f"/v1/notifications/channels/{ch_id}",
            json={"name": "Updated", "enabled": False},
            headers=tenant["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"
        assert resp.json()["enabled"] is False

    async def test_delete_channel(self, client, tenant):
        create = await client.post(
            "/v1/notifications/channels",
            json={"channel_type": "discord", "name": "Del", "config": {"webhook_url": "https://x.com"}},
            headers=tenant["headers"],
        )
        ch_id = create.json()["id"]
        resp = await client.delete(f"/v1/notifications/channels/{ch_id}", headers=tenant["headers"])
        assert resp.status_code == 204

    async def test_invalid_channel_type(self, client, tenant):
        resp = await client.post(
            "/v1/notifications/channels",
            json={"channel_type": "telegram", "name": "Bad", "config": {}},
            headers=tenant["headers"],
        )
        assert resp.status_code == 422

    async def test_no_auth(self, client):
        resp = await client.get("/v1/notifications/channels")
        assert resp.status_code in (401, 403)


class TestNotificationDispatchPreferences:
    async def test_dispatch_alert_defaults_to_enabled_channels_without_preferences(self, db_session, tenant):
        channel = NotificationChannel(
            tenant_id=tenant["tenant"].id,
            channel_type="email",
            name="Email",
            config={"email": "grower@example.com"},
            enabled=True,
        )
        db_session.add(channel)
        await db_session.commit()

        with patch("app.notifications.service._send_email", new_callable=AsyncMock) as send_email, patch(
            "app.notifications.service._send_web_push", new_callable=AsyncMock
        ) as send_web_push:
            await dispatch_alert(
                db_session,
                tenant["tenant"].id,
                "warning",
                "AI approval needed",
                "Review required",
                event_type="ai_action_lifecycle",
            )

        send_email.assert_awaited_once()
        send_web_push.assert_awaited_once()

    async def test_dispatch_alert_respects_event_type_preferences(self, db_session, tenant):
        channel = NotificationChannel(
            tenant_id=tenant["tenant"].id,
            channel_type="email",
            name="Email",
            config={"email": "grower@example.com"},
            enabled=True,
        )
        db_session.add(channel)
        await db_session.flush()

        pref = NotificationPreference(
            tenant_id=tenant["tenant"].id,
            user_id=tenant["user"].id,
            channel_id=channel.id,
            severity_filter="warning,critical",
            event_types="billing",
            enabled=True,
        )
        db_session.add(pref)
        await db_session.commit()

        with patch("app.notifications.service._send_email", new_callable=AsyncMock) as send_email, patch(
            "app.notifications.service._send_web_push", new_callable=AsyncMock
        ) as send_web_push:
            await dispatch_alert(
                db_session,
                tenant["tenant"].id,
                "warning",
                "AI approval needed",
                "Review required",
                event_type="ai_action_lifecycle",
            )

        send_email.assert_not_awaited()
        send_web_push.assert_awaited_once()
        logs = (await db_session.execute(select(NotificationLog))).scalars().all()
        assert len(logs) == 1
        assert logs[0].channel_type == "in_app"
        assert logs[0].event_type == "ai_action_lifecycle"
        assert logs[0].status == "skipped"

    async def test_dispatch_alert_sends_when_preference_allows_ai_lifecycle_event(self, db_session, tenant):
        channel = NotificationChannel(
            tenant_id=tenant["tenant"].id,
            channel_type="email",
            name="Email",
            config={"email": "grower@example.com"},
            enabled=True,
        )
        db_session.add(channel)
        await db_session.flush()

        pref = NotificationPreference(
            tenant_id=tenant["tenant"].id,
            user_id=tenant["user"].id,
            channel_id=channel.id,
            severity_filter="warning,critical",
            event_types="ai_action_lifecycle",
            enabled=True,
        )
        db_session.add(pref)
        await db_session.commit()

        with patch("app.notifications.service._send_email", new_callable=AsyncMock) as send_email, patch(
            "app.notifications.service._send_web_push", new_callable=AsyncMock
        ) as send_web_push:
            await dispatch_alert(
                db_session,
                tenant["tenant"].id,
                "warning",
                "AI approval needed",
                "Review required",
                event_type="ai_action_lifecycle",
            )

        send_email.assert_awaited_once()
        send_web_push.assert_awaited_once()
        logs = (await db_session.execute(select(NotificationLog).order_by(NotificationLog.created_at.asc()))).scalars().all()
        assert [log.channel_type for log in logs] == ["in_app", "email"]
        assert all(log.event_type == "ai_action_lifecycle" for log in logs)


class TestNotificationLogs:
    async def test_list_notification_logs_filters_ai_lifecycle_in_app_entries(self, client, db_session, tenant):
        db_session.add_all(
            [
                NotificationLog(
                    tenant_id=tenant["tenant"].id,
                    channel_type="in_app",
                    event_type="ai_action_lifecycle",
                    severity="warning",
                    subject="Approval needed",
                    body="Review a pending action.",
                    status="sent",
                ),
                NotificationLog(
                    tenant_id=tenant["tenant"].id,
                    channel_type="email",
                    event_type="billing",
                    severity="info",
                    subject="Invoice ready",
                    body="A new invoice is available.",
                    status="sent",
                ),
            ]
        )
        await db_session.commit()

        resp = await client.get(
            "/v1/notifications/logs?event_type=ai_action_lifecycle&channel_type=in_app",
            headers=tenant["headers"],
        )

        assert resp.status_code == 200
        payload = resp.json()
        assert payload["total"] == 1
        assert payload["items"][0]["subject"] == "Approval needed"
        assert payload["items"][0]["event_type"] == "ai_action_lifecycle"


# ---------- Push Subscriptions ----------


class TestPushSubscriptions:
    async def test_subscribe(self, client, tenant):
        resp = await client.post(
            "/v1/notifications/push/subscribe",
            json={
                "endpoint": "https://fcm.googleapis.com/fcm/send/test",
                "p256dh": "test-p256dh-key",
                "auth": "test-auth-key",
            },
            headers=tenant["headers"],
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "subscribed"

    async def test_unsubscribe(self, client, tenant):
        await client.post(
            "/v1/notifications/push/subscribe",
            json={"endpoint": "https://test.com", "p256dh": "k", "auth": "a"},
            headers=tenant["headers"],
        )
        resp = await client.delete("/v1/notifications/push/unsubscribe", headers=tenant["headers"])
        assert resp.status_code == 204


# ---------- Data Export ----------


class TestDataExport:
    async def test_export_bucket_not_found(self, client, tenant):
        resp = await client.get(
            f"/v1/data/export/bucket/{uuid4()}",
            headers=tenant["headers"],
        )
        assert resp.status_code == 404

    async def test_export_bucket_csv(self, client, tenant):
        # Create tent → grow → bucket → reading
        tent = await client.post("/v1/tents", json={"name": "Export Tent"}, headers=tenant["headers"])
        grow = await client.post(
            "/v1/grows",
            json={"name": "Export Grow", "tent_id": tent.json()["id"], "grow_type": "dwc"},
            headers=tenant["headers"],
        )
        bucket = await client.post(
            "/v1/buckets",
            json={"grow_cycle_id": grow.json()["id"], "position": 1, "label": "B1"},
            headers=tenant["headers"],
        )
        bucket_id = bucket.json()["id"]

        await client.post(
            "/v1/sensors",
            json={"bucket_id": bucket_id, "ph": 6.0, "ec": 1.2},
            headers=tenant["headers"],
        )

        resp = await client.get(f"/v1/data/export/bucket/{bucket_id}", headers=tenant["headers"])
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"
        assert "ph" in resp.text
        assert "6.0" in resp.text


# ---------- Billing ----------


class TestBilling:
    async def test_billing_status(self, client, tenant):
        resp = await client.get("/v1/billing/status", headers=tenant["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan"] == "free"
        assert "plan_name" in data

    async def test_checkout_invalid_plan(self, client, tenant):
        resp = await client.post(
            "/v1/billing/checkout",
            json={"plan": "nonexistent"},
            headers=tenant["headers"],
        )
        assert resp.status_code == 400

    async def test_portal_no_stripe(self, client, tenant):
        resp = await client.post("/v1/billing/portal", headers=tenant["headers"])
        assert resp.status_code == 400  # No stripe customer

    async def test_billing_no_auth(self, client):
        resp = await client.get("/v1/billing/status")
        assert resp.status_code in (401, 403)
