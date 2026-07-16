"""Tests for connector persist_readings() and scheduler wiring."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.integrations.connectors.base import BaseConnector, ConnectorResult
from app.integrations.connectors.ecowitt import EcowittConnector
from app.integrations.connectors.openweather import OpenWeatherConnector
from app.integrations.connectors.pulse import PulseConnector
from app.integrations.models import IntegrationConfig, IntegrationDeviceMap

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(type_: str = "pulse", tenant_id=None) -> IntegrationConfig:
    return IntegrationConfig(
        id=uuid4(),
        tenant_id=tenant_id or uuid4(),
        type=type_,
        name=f"Test {type_}",
        config="encrypted-placeholder",
        webhook_secret="test-secret",
        enabled=True,
        poll_interval_s=300,
    )


def _make_device_map(integration_id, tenant_id, external_id="dev1", **kw) -> IntegrationDeviceMap:
    return IntegrationDeviceMap(
        id=uuid4(),
        tenant_id=tenant_id,
        integration_id=integration_id,
        external_id=external_id,
        external_name=f"Device {external_id}",
        tent_id=kw.get("tent_id", uuid4()),
        bucket_id=kw.get("bucket_id"),
        sensor_mapping=kw.get("sensor_mapping", {}),
        enabled=True,
    )


def _mock_session_factory(mock_session):
    """Return a callable that yields an async context manager wrapping mock_session."""

    @asynccontextmanager
    async def _factory():
        yield mock_session

    return _factory


# ---------------------------------------------------------------------------
# BaseConnector default persist_readings returns 0
# ---------------------------------------------------------------------------


class TestBaseConnectorDefault:
    async def test_default_persist_returns_zero(self):
        """BaseConnector.persist_readings returns 0 (no-op)."""

        # Create a concrete subclass for testing the default
        class StubConnector(BaseConnector):
            integration_type = "stub"

            async def poll(self) -> ConnectorResult:
                return ConnectorResult()

            async def handle_webhook(self, payload: dict[str, Any]) -> ConnectorResult:
                return ConnectorResult()

        cfg = _make_config("stub")
        connector = StubConnector(config=cfg, decrypted_config={}, device_maps=[])
        result = ConnectorResult()
        result.readings.append({"some": "data"})

        session = AsyncMock()
        count = await connector.persist_readings(session, result)
        assert count == 0


# ---------------------------------------------------------------------------
# PulseConnector.persist_readings
# ---------------------------------------------------------------------------


class TestPulsePersistReadings:
    async def test_delegates_to_write_pulse_readings(self):
        cfg = _make_config("pulse")
        connector = PulseConnector(
            config=cfg,
            decrypted_config={"email": "a@b.com", "password": "pw"},
            device_maps=[],
        )
        result = ConnectorResult()
        result.readings.extend(
            [
                {
                    "target": "tent",
                    "external_id": "d1",
                    "tenant_id": str(cfg.tenant_id),
                    "tent_id": str(uuid4()),
                    "ambient_temp_f": 75.0,
                },
            ]
        )

        session = AsyncMock()
        with patch(
            "app.integrations.connectors.pulse.write_pulse_readings", new_callable=AsyncMock, return_value=1
        ) as mock_write:
            count = await connector.persist_readings(session, result)
            mock_write.assert_awaited_once_with(session, result.readings)
            assert count == 1


# ---------------------------------------------------------------------------
# OpenWeatherConnector.persist_readings
# ---------------------------------------------------------------------------


class TestOpenWeatherPersistReadings:
    async def test_delegates_to_write_openweather_readings(self):
        cfg = _make_config("openweather")
        connector = OpenWeatherConnector(
            config=cfg,
            decrypted_config={"api_key": "test-key-12345"},
            device_maps=[],
        )
        result = ConnectorResult()
        result.readings.extend(
            [
                {"tenant_id": str(cfg.tenant_id), "tent_id": str(uuid4()), "temperature_c": 22.0},
            ]
        )

        session = AsyncMock()
        with patch(
            "app.integrations.connectors.openweather.write_openweather_readings", new_callable=AsyncMock, return_value=1
        ) as mock_write:
            count = await connector.persist_readings(session, result)
            mock_write.assert_awaited_once_with(session, result.readings)
            assert count == 1


# ---------------------------------------------------------------------------
# EcowittConnector.persist_readings
# ---------------------------------------------------------------------------


class TestEcowittPersistReadings:
    async def test_delegates_to_write_ecowitt_readings(self):
        cfg = _make_config("ecowitt")
        connector = EcowittConnector(
            config=cfg,
            decrypted_config={"mode": "cloud", "application_key": "ak", "api_key": "apikey", "mac": "AA:BB:CC"},
            device_maps=[],
        )
        result = ConnectorResult()
        result.readings.extend(
            [
                {"target": "weather", "tenant_id": str(cfg.tenant_id), "tent_id": str(uuid4()), "temperature_c": 18.0},
            ]
        )

        session = AsyncMock()
        with patch(
            "app.integrations.connectors.ecowitt.write_ecowitt_readings", new_callable=AsyncMock, return_value=1
        ) as mock_write:
            count = await connector.persist_readings(session, result)
            mock_write.assert_awaited_once_with(session, result.readings)
            assert count == 1


# ---------------------------------------------------------------------------
# Scheduler _integration_poll calls persist_readings
# ---------------------------------------------------------------------------


class TestSchedulerPersistence:
    async def test_integration_poll_calls_persist_readings(self):
        """The scheduler's _integration_poll persists readings after a successful poll."""
        from app.scheduler.tasks import TaskRunner

        poll_result = ConnectorResult()
        poll_result.readings.append({"some": "reading"})

        mock_connector = AsyncMock()
        mock_connector.poll = AsyncMock(return_value=poll_result)
        mock_connector.persist_readings = AsyncMock(return_value=1)
        mock_connector.write_sync_log = AsyncMock()

        cfg = _make_config("pulse")
        cfg.last_synced_at = None
        cfg.error_count = 0

        dm = _make_device_map(cfg.id, cfg.tenant_id)

        mock_session = AsyncMock()
        # Make execute() return configs, then RLS SET, then device maps
        configs_result = MagicMock()
        configs_result.scalars.return_value.all.return_value = [cfg]
        dm_result = MagicMock()
        dm_result.scalars.return_value.all.return_value = [dm]
        mock_session.execute = AsyncMock(side_effect=[configs_result, MagicMock(), dm_result])

        mock_connector_cls = MagicMock(return_value=mock_connector)

        with (
            patch("app.database.async_session_factory", _mock_session_factory(mock_session)),
            patch("app.integrations.connectors.base.get_connector_class", return_value=mock_connector_cls),
            patch("app.integrations.crypto.decrypt_config", return_value={"key": "val"}),
        ):
            runner = TaskRunner(settings=MagicMock())
            await runner._integration_poll()

        # Verify persist_readings was called
        mock_connector.persist_readings.assert_awaited_once_with(mock_session, poll_result)
        mock_connector.write_sync_log.assert_awaited_once()

    async def test_integration_poll_skips_persist_on_empty_readings(self):
        """persist_readings is not called when poll returns no readings."""
        from app.scheduler.tasks import TaskRunner

        poll_result = ConnectorResult()  # No readings

        mock_connector = AsyncMock()
        mock_connector.poll = AsyncMock(return_value=poll_result)
        mock_connector.persist_readings = AsyncMock()
        mock_connector.write_sync_log = AsyncMock()

        cfg = _make_config("pulse")
        cfg.last_synced_at = None
        cfg.error_count = 0

        mock_session = AsyncMock()
        configs_result = MagicMock()
        configs_result.scalars.return_value.all.return_value = [cfg]
        dm_result = MagicMock()
        dm_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(side_effect=[configs_result, MagicMock(), dm_result])

        mock_connector_cls = MagicMock(return_value=mock_connector)

        with (
            patch("app.database.async_session_factory", _mock_session_factory(mock_session)),
            patch("app.integrations.connectors.base.get_connector_class", return_value=mock_connector_cls),
            patch("app.integrations.crypto.decrypt_config", return_value={}),
        ):
            runner = TaskRunner(settings=MagicMock())
            await runner._integration_poll()

        mock_connector.persist_readings.assert_not_awaited()

    async def test_persist_failure_adds_error_to_result(self):
        """If persist_readings raises, the error is captured in the result."""
        from app.scheduler.tasks import TaskRunner

        poll_result = ConnectorResult()
        poll_result.readings.append({"data": 1})

        mock_connector = AsyncMock()
        mock_connector.poll = AsyncMock(return_value=poll_result)
        mock_connector.persist_readings = AsyncMock(side_effect=RuntimeError("DB down"))
        mock_connector.write_sync_log = AsyncMock()

        cfg = _make_config("pulse")
        cfg.last_synced_at = None
        cfg.error_count = 0

        mock_session = AsyncMock()
        configs_result = MagicMock()
        configs_result.scalars.return_value.all.return_value = [cfg]
        dm_result = MagicMock()
        dm_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(side_effect=[configs_result, MagicMock(), dm_result])

        mock_connector_cls = MagicMock(return_value=mock_connector)

        with (
            patch("app.database.async_session_factory", _mock_session_factory(mock_session)),
            patch("app.integrations.connectors.base.get_connector_class", return_value=mock_connector_cls),
            patch("app.integrations.crypto.decrypt_config", return_value={}),
        ):
            runner = TaskRunner(settings=MagicMock())
            await runner._integration_poll()

        # Sync log should still be written with error captured
        mock_connector.write_sync_log.assert_awaited_once()
        assert "Reading persistence failed" in poll_result.errors


class TestSchedulerProactiveCoaching:
    async def test_proactive_coaching_sends_low_health_alert(self):
        """Low recent health score should trigger one coaching notification."""
        from app.scheduler.tasks import TaskRunner

        grow = MagicMock()
        grow.id = uuid4()
        grow.tenant_id = uuid4()
        grow.name = "Room A"
        grow.stage = "vegetative"

        latest_eval = MagicMock()
        latest_eval.score = 55
        latest_eval.created_at = datetime.now(UTC)

        mock_session = MagicMock()
        grows_result = MagicMock()
        grows_result.scalars.return_value.all.return_value = [grow]
        settings_result = MagicMock()
        settings_result.all.return_value = [
            (grow.tenant_id, {"enabled": True, "cadence_hours": 24, "minimum_severity": "info"})
        ]
        eval_result = MagicMock()
        eval_result.scalar_one_or_none.return_value = latest_eval
        cooldown_result = MagicMock()
        cooldown_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(side_effect=[grows_result, settings_result, eval_result, cooldown_result])
        mock_session.commit = AsyncMock()

        with (
            patch("app.database.async_session_factory", _mock_session_factory(mock_session)),
            patch("app.notifications.service.dispatch_alert", new_callable=AsyncMock) as mock_dispatch,
        ):
            runner = TaskRunner(settings=MagicMock())
            await runner._proactive_coaching()

        mock_dispatch.assert_awaited_once()
        call_args = mock_dispatch.await_args
        assert call_args.kwargs["event_type"] == "ai_coaching"
        assert "Low Health Score Follow-Up" in call_args.args[3]
        mock_session.add.assert_called_once()

    async def test_proactive_coaching_respects_cooldown(self):
        """Recent matching coaching alert should suppress duplicates."""
        from app.scheduler.tasks import TaskRunner

        grow = MagicMock()
        grow.id = uuid4()
        grow.tenant_id = uuid4()
        grow.name = "Room A"
        grow.stage = "flowering"

        latest_eval = MagicMock()
        latest_eval.score = 80
        latest_eval.created_at = datetime.now(UTC)

        existing_alert = MagicMock()

        mock_session = MagicMock()
        grows_result = MagicMock()
        grows_result.scalars.return_value.all.return_value = [grow]
        settings_result = MagicMock()
        settings_result.all.return_value = [
            (grow.tenant_id, {"enabled": True, "cadence_hours": 24, "minimum_severity": "info"})
        ]
        eval_result = MagicMock()
        eval_result.scalar_one_or_none.return_value = latest_eval
        cooldown_result = MagicMock()
        cooldown_result.scalar_one_or_none.return_value = existing_alert
        mock_session.execute = AsyncMock(side_effect=[grows_result, settings_result, eval_result, cooldown_result])
        mock_session.commit = AsyncMock()

        with (
            patch("app.database.async_session_factory", _mock_session_factory(mock_session)),
            patch("app.notifications.service.dispatch_alert", new_callable=AsyncMock) as mock_dispatch,
        ):
            runner = TaskRunner(settings=MagicMock())
            await runner._proactive_coaching()

        mock_dispatch.assert_not_awaited()
        mock_session.add.assert_not_called()


class TestSchedulerVisionAutoScan:
    async def test_vision_auto_scan_persists_detections(self):
        """Scheduled vision scans persist detections for active grows."""
        from app.scheduler.tasks import TaskRunner
        from app.vision.contracts import AcceleratorTier, BoundingBox, VisionDetection
        from app.vision.service import DetectionResponse

        grow = MagicMock()
        grow.id = uuid4()
        grow.tenant_id = uuid4()
        grow.settings = None
        grow.tent_id = uuid4()

        tent = MagicMock()
        tent.id = uuid4()
        tent.camera_url = "http://camera/snapshot.jpg"

        tenant = MagicMock()
        tenant.coaching_settings = {
            "vision_auto_scan": {
                "enabled": True,
                "cadence_minutes": 60,
                "confidence_task_threshold": 0.9,
                "task_cooldown_hours": 12,
            }
        }

        camera = MagicMock()
        camera.url = "http://camera/snapshot.jpg"
        camera.camera_type = "http_snapshot"

        detection = VisionDetection(
            class_name="cannabis",
            confidence=0.99,
            bbox=BoundingBox(x=1.0, y=2.0, width=3.0, height=4.0),
        )
        model_response = DetectionResponse(
            model_version="v-test",
            accelerator_tier=AcceleratorTier.CORAL,
            detections=(detection,),
            message=None,
        )

        mock_client = AsyncMock()
        mock_client.scan_image = AsyncMock(return_value=model_response)

        mock_session = MagicMock()
        grows_result = MagicMock()
        grows_result.all.return_value = [(grow, tent, tenant)]
        camera_result = MagicMock()
        camera_result.scalar_one_or_none.return_value = camera
        owner_result = MagicMock()
        owner_result.scalar_one_or_none.return_value = uuid4()
        existing_task_result = MagicMock()
        existing_task_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(side_effect=[grows_result, camera_result, owner_result, existing_task_result])
        mock_session.commit = AsyncMock()

        with (
            patch("app.database.async_session_factory", _mock_session_factory(mock_session)),
            patch("app.vision.client.VisionDetectorClient.from_settings", return_value=mock_client),
            patch("app.grows.tent_routes._fetch_camera_image", new_callable=AsyncMock, return_value=b"img"),
        ):
            runner = TaskRunner(settings=MagicMock())
            await runner._vision_auto_scan()

        mock_client.scan_image.assert_awaited_once()
        mock_session.add_all.assert_called_once()
        mock_session.commit.assert_awaited_once()
