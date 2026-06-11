"""Tests for the equipment control module."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from app.equipment.interlocks import (
    RAPID_CYCLE_MAX,
    check_max_on_violations,
    validate_interlocks,
)
from app.equipment.models import (
    CAPABILITIES,
    EQUIPMENT_TYPES,
    PROTOCOLS,
    ControllableEquipment,
    EquipmentStateLog,
)
from app.equipment.protocols.dispatch import DispatchResult
from app.equipment.protocols.generic_mqtt import parse_generic_state
from app.equipment.protocols.tasmota import parse_tasmota_result, parse_tasmota_sensor
from app.equipment.schemas import EquipmentCommand, EquipmentCreate, EquipmentUpdate
from app.equipment.service import (
    _compute_new_state,
    confirm_equipment_state,
    execute_equipment_command,
    force_off_equipment,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── Schema Validation Tests ────────────────────────────────────────────────────


class TestSchemas:
    """Test Pydantic schema validation."""

    def test_valid_create(self):
        schema = EquipmentCreate(
            name="Exhaust Fan",
            equipment_type="fan_controller",
            protocol="tasmota_mqtt",
            protocol_config={"mqtt_topic": "fan_exhaust"},
            capabilities=["on_off"],
        )
        assert schema.name == "Exhaust Fan"
        assert schema.equipment_type == "fan_controller"
        assert schema.cooldown_minutes == 0

    def test_invalid_equipment_type(self):
        with pytest.raises(ValueError, match="Invalid equipment_type"):
            EquipmentCreate(
                name="Test",
                equipment_type="invalid_type",
                protocol="tasmota_mqtt",
            )

    def test_invalid_protocol(self):
        with pytest.raises(ValueError, match="Invalid protocol"):
            EquipmentCreate(
                name="Test",
                equipment_type="relay",
                protocol="invalid_protocol",
            )

    def test_invalid_capabilities(self):
        with pytest.raises(ValueError, match="Invalid capabilities"):
            EquipmentCreate(
                name="Test",
                equipment_type="relay",
                protocol="tasmota_mqtt",
                capabilities=["on_off", "teleport"],
            )

    def test_invalid_max_on(self):
        with pytest.raises(ValueError, match="max_on_minutes must be at least 1"):
            EquipmentCreate(
                name="Test",
                equipment_type="relay",
                protocol="tasmota_mqtt",
                max_on_minutes=0,
            )

    def test_invalid_cooldown(self):
        with pytest.raises(ValueError, match="cooldown_minutes must be non-negative"):
            EquipmentCreate(
                name="Test",
                equipment_type="relay",
                protocol="tasmota_mqtt",
                cooldown_minutes=-1,
            )

    def test_command_valid_actions(self):
        for action in ("on", "off", "toggle", "set_brightness"):
            cmd = EquipmentCommand(action=action)
            assert cmd.action == action

    def test_command_invalid_action(self):
        with pytest.raises(ValueError, match="Invalid action"):
            EquipmentCommand(action="explode")

    def test_command_brightness_range(self):
        with pytest.raises(ValueError, match="value must be between 0 and 100"):
            EquipmentCommand(action="set_brightness", value=150)

    def test_update_partial(self):
        update = EquipmentUpdate(name="New Name")
        data = update.model_dump(exclude_unset=True)
        assert data == {"name": "New Name"}


# ── Protocol Parser Tests ──────────────────────────────────────────────────────


class TestTasmotaParsers:
    """Test Tasmota message parsing."""

    def test_parse_result_power_on(self):
        state = parse_tasmota_result({"POWER": "ON"})
        assert state == {"is_on": True}

    def test_parse_result_power_off(self):
        state = parse_tasmota_result({"POWER": "OFF"})
        assert state == {"is_on": False}

    def test_parse_result_with_dimmer(self):
        state = parse_tasmota_result({"POWER": "ON", "Dimmer": "75"})
        assert state == {"is_on": True, "brightness": 75}

    def test_parse_result_empty(self):
        state = parse_tasmota_result({"Time": "2026-06-11T10:00:00"})
        assert state == {}

    def test_parse_sensor_energy(self):
        payload = {
            "ENERGY": {
                "Power": 120,
                "Voltage": 230,
                "Current": 0.52,
                "Total": 12.345,
            }
        }
        state = parse_tasmota_sensor(payload)
        assert state["power_w"] == 120.0
        assert state["voltage_v"] == 230.0
        assert state["current_ma"] == 520.0
        assert state["energy_kwh"] == 12.345

    def test_parse_sensor_empty(self):
        state = parse_tasmota_sensor({"Time": "2026-06-11T10:00:00"})
        assert state == {}

    def test_parse_sensor_partial_energy(self):
        state = parse_tasmota_sensor({"ENERGY": {"Power": 0}})
        assert state == {"power_w": 0.0}


class TestGenericMqttParser:
    """Test generic MQTT state parsing."""

    def test_parse_on_payload(self):
        config = {"on_payload": "ON", "off_payload": "OFF"}
        state = parse_generic_state("ON", config)
        assert state == {"is_on": True}

    def test_parse_off_payload(self):
        config = {"on_payload": "ON", "off_payload": "OFF"}
        state = parse_generic_state("OFF", config)
        assert state == {"is_on": False}

    def test_parse_brightness_value(self):
        config = {"on_payload": "ON", "off_payload": "OFF", "brightness_range": [0, 255]}
        state = parse_generic_state("128", config)
        assert state["is_on"] is True
        assert 49 <= state["brightness"] <= 51  # ~50%

    def test_parse_zero_brightness(self):
        config = {"on_payload": "ON", "off_payload": "OFF", "brightness_range": [0, 100]}
        state = parse_generic_state("0", config)
        assert state == {"is_on": False, "brightness": 0}

    def test_parse_unknown_payload(self):
        config = {"on_payload": "ON", "off_payload": "OFF"}
        state = parse_generic_state("UNKNOWN", config)
        assert state == {}

    def test_parse_custom_payloads(self):
        config = {"on_payload": "1", "off_payload": "0"}
        assert parse_generic_state("1", config) == {"is_on": True}
        assert parse_generic_state("0", config) == {"is_on": False}


# ── State Computation Tests ────────────────────────────────────────────────────


class TestStateComputation:
    """Test state transition logic."""

    def test_on_from_off(self):
        state = _compute_new_state({"is_on": False}, "on", None)
        assert state == {"is_on": True}

    def test_off_from_on(self):
        state = _compute_new_state({"is_on": True}, "off", None)
        assert state == {"is_on": False}

    def test_toggle_from_off(self):
        state = _compute_new_state({"is_on": False}, "toggle", None)
        assert state == {"is_on": True}

    def test_toggle_from_on(self):
        state = _compute_new_state({"is_on": True}, "toggle", None)
        assert state == {"is_on": False}

    def test_set_brightness(self):
        state = _compute_new_state({"is_on": False}, "set_brightness", 75)
        assert state == {"is_on": True, "brightness": 75}

    def test_set_brightness_zero(self):
        state = _compute_new_state({"is_on": True, "brightness": 50}, "set_brightness", 0)
        assert state == {"is_on": False, "brightness": 0}

    def test_preserves_other_fields(self):
        state = _compute_new_state({"is_on": False, "power_w": 120}, "on", None)
        assert state == {"is_on": True, "power_w": 120}


# ── Interlock Tests ────────────────────────────────────────────────────────────


class TestInterlocks:
    """Test safety interlock validation."""

    async def test_off_action_always_allowed(self, db_session):
        equip = _make_equipment(cooldown_minutes=999)
        result = await validate_interlocks(db_session, equip, "off")
        assert result.allowed is True

    async def test_no_interlocks_pass(self, db_session):
        equip = _make_equipment()
        result = await validate_interlocks(db_session, equip, "on")
        assert result.allowed is True

    async def test_cooldown_blocks(self, db_session):
        equip = _make_equipment(cooldown_minutes=10)
        db_session.add(equip)
        await db_session.flush()

        # Add a recent OFF log
        log = EquipmentStateLog(
            tenant_id=equip.tenant_id,
            equipment_id=equip.id,
            action="off",
            source="user",
            created_at=datetime.now(UTC) - timedelta(minutes=5),
        )
        db_session.add(log)
        await db_session.flush()

        result = await validate_interlocks(db_session, equip, "on")
        assert result.allowed is False
        assert result.violation == "cooldown"
        assert result.details["remaining_minutes"] > 0

    async def test_cooldown_expired_allows(self, db_session):
        equip = _make_equipment(cooldown_minutes=5)
        db_session.add(equip)
        await db_session.flush()

        # Add an old OFF log (beyond cooldown)
        log = EquipmentStateLog(
            tenant_id=equip.tenant_id,
            equipment_id=equip.id,
            action="off",
            source="user",
            created_at=datetime.now(UTC) - timedelta(minutes=10),
        )
        db_session.add(log)
        await db_session.flush()

        result = await validate_interlocks(db_session, equip, "on")
        assert result.allowed is True

    async def test_conflict_blocks(self, db_session):
        # Create two equipment that conflict with each other
        equip_a = _make_equipment(name="Heater")
        equip_a.requested_state = {"is_on": True}
        db_session.add(equip_a)
        await db_session.flush()

        equip_b = _make_equipment(name="AC Unit")
        equip_b.conflicts_with = [equip_a.id]
        db_session.add(equip_b)
        await db_session.flush()

        result = await validate_interlocks(db_session, equip_b, "on")
        assert result.allowed is False
        assert result.violation == "conflict"
        assert any(c["name"] == "Heater" for c in result.details["active_conflicts"])

    async def test_conflict_allows_when_inactive(self, db_session):
        equip_a = _make_equipment(name="Heater")
        equip_a.requested_state = {"is_on": False}
        db_session.add(equip_a)
        await db_session.flush()

        equip_b = _make_equipment(name="AC Unit")
        equip_b.conflicts_with = [equip_a.id]
        db_session.add(equip_b)
        await db_session.flush()

        result = await validate_interlocks(db_session, equip_b, "on")
        assert result.allowed is True

    async def test_rapid_cycling_blocks(self, db_session):
        equip = _make_equipment()
        db_session.add(equip)
        await db_session.flush()

        # Add many toggles in rapid succession
        now = datetime.now(UTC)
        for i in range(RAPID_CYCLE_MAX):
            log = EquipmentStateLog(
                tenant_id=equip.tenant_id,
                equipment_id=equip.id,
                action="on" if i % 2 == 0 else "off",
                source="user",
                created_at=now - timedelta(seconds=i * 10),
            )
            db_session.add(log)
        await db_session.flush()

        result = await validate_interlocks(db_session, equip, "on")
        assert result.allowed is False
        assert result.violation == "rapid_cycling"

    async def test_max_on_violation_detection(self, db_session):
        equip = _make_equipment(max_on_minutes=30)
        equip.requested_state = {"is_on": True}
        db_session.add(equip)
        await db_session.flush()

        # Add an ON log from 45 minutes ago (exceeds 30 min limit)
        log = EquipmentStateLog(
            tenant_id=equip.tenant_id,
            equipment_id=equip.id,
            action="on",
            source="user",
            created_at=datetime.now(UTC) - timedelta(minutes=45),
        )
        db_session.add(log)
        await db_session.flush()

        violations = await check_max_on_violations(db_session, equip.tenant_id)
        assert len(violations) == 1
        assert violations[0].id == equip.id

    async def test_max_on_no_violation_when_under_limit(self, db_session):
        equip = _make_equipment(max_on_minutes=60)
        equip.requested_state = {"is_on": True}
        db_session.add(equip)
        await db_session.flush()

        log = EquipmentStateLog(
            tenant_id=equip.tenant_id,
            equipment_id=equip.id,
            action="on",
            source="user",
            created_at=datetime.now(UTC) - timedelta(minutes=30),
        )
        db_session.add(log)
        await db_session.flush()

        violations = await check_max_on_violations(db_session, equip.tenant_id)
        assert len(violations) == 0


# ── Service Tests ──────────────────────────────────────────────────────────────


class TestEquipmentService:
    """Test the equipment control service."""

    @patch("app.equipment.protocols.dispatch.dispatch_command")
    async def test_execute_command_success(self, mock_dispatch, db_session):
        mock_dispatch.return_value = DispatchResult(success=True, message="OK")

        equip = _make_equipment()
        equip.requested_state = {"is_on": False}
        db_session.add(equip)
        await db_session.flush()

        success, _message, _details = await execute_equipment_command(
            session=db_session,
            equipment=equip,
            action="on",
            source="user",
        )

        assert success is True
        assert equip.requested_state == {"is_on": True}
        mock_dispatch.assert_called_once()

    @patch("app.equipment.protocols.dispatch.dispatch_command")
    async def test_execute_command_dispatch_failure(self, mock_dispatch, db_session):
        mock_dispatch.return_value = DispatchResult(success=False, message="Connection refused")

        equip = _make_equipment()
        equip.requested_state = {"is_on": False}
        db_session.add(equip)
        await db_session.flush()

        success, message, _ = await execute_equipment_command(
            session=db_session,
            equipment=equip,
            action="on",
            source="user",
        )

        assert success is False
        assert "Connection refused" in message

    @patch("app.equipment.protocols.dispatch.dispatch_command")
    async def test_execute_command_logs_state(self, mock_dispatch, db_session):
        mock_dispatch.return_value = DispatchResult(success=True, message="OK")

        equip = _make_equipment()
        equip.requested_state = {"is_on": False}
        db_session.add(equip)
        await db_session.flush()

        await execute_equipment_command(db_session, equip, "on", source="automation")
        await db_session.flush()

        # Check state log was created
        from sqlalchemy import select

        logs = (
            (await db_session.execute(select(EquipmentStateLog).where(EquipmentStateLog.equipment_id == equip.id)))
            .scalars()
            .all()
        )
        assert len(logs) == 1
        assert logs[0].action == "on"
        assert logs[0].source == "automation"
        assert logs[0].state_before == {"is_on": False}
        assert logs[0].state_after == {"is_on": True}

    async def test_confirm_state(self, db_session):
        equip = _make_equipment()
        equip.confirmed_state = {"is_on": False}
        db_session.add(equip)
        await db_session.flush()

        await confirm_equipment_state(db_session, equip, {"is_on": True, "power_w": 120.0})

        assert equip.confirmed_state == {"is_on": True, "power_w": 120.0}
        assert equip.last_confirmed_at is not None

    @patch("app.equipment.protocols.dispatch.dispatch_command")
    async def test_force_off(self, mock_dispatch, db_session):
        mock_dispatch.return_value = DispatchResult(success=True, message="OFF sent")

        equip = _make_equipment()
        equip.requested_state = {"is_on": True}
        db_session.add(equip)
        await db_session.flush()

        result = await force_off_equipment(db_session, equip, reason="max_on exceeded")

        assert result.success is True
        assert equip.requested_state == {"is_on": False}


# ── Protocol Dispatch Tests ────────────────────────────────────────────────────


class TestProtocolDispatch:
    """Test protocol adapter dispatch."""

    @patch("app.mqtt.publisher.publish_command", new_callable=AsyncMock)
    async def test_tasmota_on(self, mock_publish):
        from app.equipment.protocols.tasmota import handle_command

        equip = _make_equipment(protocol="tasmota_mqtt")
        equip.protocol_config = {"mqtt_topic": "test_plug"}

        result = await handle_command(equip, "on")
        assert result.success is True
        mock_publish.assert_called_once_with("cmnd/test_plug/Power", "ON")

    @patch("app.mqtt.publisher.publish_command", new_callable=AsyncMock)
    async def test_tasmota_off(self, mock_publish):
        from app.equipment.protocols.tasmota import handle_command

        equip = _make_equipment(protocol="tasmota_mqtt")
        equip.protocol_config = {"mqtt_topic": "test_plug"}

        result = await handle_command(equip, "off")
        assert result.success is True
        mock_publish.assert_called_once_with("cmnd/test_plug/Power", "OFF")

    @patch("app.mqtt.publisher.publish_command", new_callable=AsyncMock)
    async def test_tasmota_dimmer(self, mock_publish):
        from app.equipment.protocols.tasmota import handle_command

        equip = _make_equipment(protocol="tasmota_mqtt")
        equip.protocol_config = {"mqtt_topic": "light_1"}

        result = await handle_command(equip, "set_brightness", 75)
        assert result.success is True
        mock_publish.assert_called_once_with("cmnd/light_1/Dimmer", "75")

    @patch("app.mqtt.publisher.publish_command", new_callable=AsyncMock)
    async def test_tasmota_channel(self, mock_publish):
        from app.equipment.protocols.tasmota import handle_command

        equip = _make_equipment(protocol="tasmota_mqtt")
        equip.protocol_config = {"mqtt_topic": "multi_relay", "channel": "2"}

        result = await handle_command(equip, "on")
        assert result.success is True
        mock_publish.assert_called_once_with("cmnd/multi_relay/Power2", "ON")

    @patch("app.mqtt.publisher.publish_command", new_callable=AsyncMock)
    async def test_generic_mqtt_on(self, mock_publish):
        from app.equipment.protocols.generic_mqtt import handle_command

        equip = _make_equipment(protocol="generic_mqtt")
        equip.protocol_config = {
            "command_topic": "home/fan/set",
            "on_payload": "1",
            "off_payload": "0",
        }

        result = await handle_command(equip, "on")
        assert result.success is True
        mock_publish.assert_called_once_with("home/fan/set", "1")

    @patch("app.mqtt.publisher.publish_command", new_callable=AsyncMock)
    async def test_generic_mqtt_brightness(self, mock_publish):
        from app.equipment.protocols.generic_mqtt import handle_command

        equip = _make_equipment(protocol="generic_mqtt")
        equip.protocol_config = {
            "command_topic": "home/light/set",
            "brightness_topic": "home/light/brightness",
            "brightness_range": [0, 255],
        }

        result = await handle_command(equip, "set_brightness", 50)
        assert result.success is True
        # 50% of 255 = 127
        mock_publish.assert_called_once_with("home/light/brightness", "127")

    def test_tasmota_missing_topic(self):
        """Sync wrapper to test missing config."""
        import asyncio

        from app.equipment.protocols.tasmota import handle_command

        equip = _make_equipment(protocol="tasmota_mqtt")
        equip.protocol_config = {}

        result = asyncio.get_event_loop().run_until_complete(handle_command(equip, "on"))
        assert result.success is False
        assert "Missing mqtt_topic" in result.message


# ── API Route Tests ────────────────────────────────────────────────────────────


class TestEquipmentAPI:
    """Test equipment API routes end-to-end."""

    async def test_create_equipment(self, client, db_session):
        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")

        resp = await client.post(
            "/v1/equipment/",
            json={
                "name": "Exhaust Fan",
                "equipment_type": "fan_controller",
                "protocol": "tasmota_mqtt",
                "protocol_config": {"mqtt_topic": "exhaust_1"},
                "capabilities": ["on_off"],
                "max_on_minutes": 720,
                "cooldown_minutes": 5,
            },
            headers={"Authorization": f"Bearer {tenant_data['token']}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Exhaust Fan"
        assert data["protocol"] == "tasmota_mqtt"
        assert data["requested_state"] == {"is_on": False}

    async def test_list_equipment(self, client, db_session):
        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")
        headers = {"Authorization": f"Bearer {tenant_data['token']}"}

        # Create two equipment
        await client.post(
            "/v1/equipment/",
            json={
                "name": "Fan A",
                "equipment_type": "relay",
                "protocol": "tasmota_mqtt",
                "protocol_config": {"mqtt_topic": "a"},
            },
            headers=headers,
        )
        await client.post(
            "/v1/equipment/",
            json={
                "name": "Fan B",
                "equipment_type": "relay",
                "protocol": "shelly_http",
                "protocol_config": {"ip_address": "192.168.1.2"},
            },
            headers=headers,
        )

        resp = await client.get("/v1/equipment/", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    async def test_update_equipment(self, client, db_session):
        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")
        headers = {"Authorization": f"Bearer {tenant_data['token']}"}

        resp = await client.post(
            "/v1/equipment/",
            json={
                "name": "Old Name",
                "equipment_type": "relay",
                "protocol": "tasmota_mqtt",
                "protocol_config": {"mqtt_topic": "x"},
            },
            headers=headers,
        )
        equip_id = resp.json()["id"]

        resp = await client.patch(
            f"/v1/equipment/{equip_id}",
            json={"name": "New Name", "cooldown_minutes": 10},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        assert resp.json()["cooldown_minutes"] == 10

    async def test_delete_equipment(self, client, db_session):
        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")
        headers = {"Authorization": f"Bearer {tenant_data['token']}"}

        resp = await client.post(
            "/v1/equipment/",
            json={
                "name": "To Delete",
                "equipment_type": "relay",
                "protocol": "generic_mqtt",
                "protocol_config": {"command_topic": "t"},
            },
            headers=headers,
        )
        equip_id = resp.json()["id"]

        resp = await client.delete(f"/v1/equipment/{equip_id}", headers=headers)
        assert resp.status_code == 204

        resp = await client.get(f"/v1/equipment/{equip_id}", headers=headers)
        assert resp.status_code == 404

    @patch("app.equipment.protocols.dispatch.dispatch_command")
    async def test_send_command(self, mock_dispatch, client, db_session):
        mock_dispatch.return_value = DispatchResult(success=True, message="Sent")

        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")
        headers = {"Authorization": f"Bearer {tenant_data['token']}"}

        resp = await client.post(
            "/v1/equipment/",
            json={
                "name": "Plug",
                "equipment_type": "smart_plug",
                "protocol": "tasmota_mqtt",
                "protocol_config": {"mqtt_topic": "p1"},
            },
            headers=headers,
        )
        equip_id = resp.json()["id"]

        resp = await client.post(
            f"/v1/equipment/{equip_id}/command",
            json={"action": "on"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["requested_state"]["is_on"] is True

    async def test_send_command_disabled(self, client, db_session):
        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")
        headers = {"Authorization": f"Bearer {tenant_data['token']}"}

        resp = await client.post(
            "/v1/equipment/",
            json={
                "name": "Disabled",
                "equipment_type": "relay",
                "protocol": "tasmota_mqtt",
                "protocol_config": {"mqtt_topic": "d"},
            },
            headers=headers,
        )
        equip_id = resp.json()["id"]

        # Disable it
        await client.patch(f"/v1/equipment/{equip_id}", json={"enabled": False}, headers=headers)

        resp = await client.post(
            f"/v1/equipment/{equip_id}/command",
            json={"action": "on"},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "disabled" in resp.json()["detail"]

    async def test_equipment_not_found(self, client, db_session):
        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")
        headers = {"Authorization": f"Bearer {tenant_data['token']}"}

        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/v1/equipment/{fake_id}", headers=headers)
        assert resp.status_code == 404

    async def test_invalid_equipment_id(self, client, db_session):
        from tests.conftest import TenantFactory

        factory = TenantFactory(db_session)
        tenant_data = await factory.create(plan="pro")
        headers = {"Authorization": f"Bearer {tenant_data['token']}"}

        resp = await client.get("/v1/equipment/not-a-uuid", headers=headers)
        assert resp.status_code == 400


# ── Model Constants Tests ──────────────────────────────────────────────────────


class TestModelConstants:
    """Verify model constants are consistent."""

    def test_equipment_types_non_empty(self):
        assert len(EQUIPMENT_TYPES) >= 5

    def test_protocols_non_empty(self):
        assert len(PROTOCOLS) >= 4

    def test_capabilities_non_empty(self):
        assert len(CAPABILITIES) >= 3


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_equipment(
    name: str = "Test Equipment",
    protocol: str = "tasmota_mqtt",
    max_on_minutes: int | None = None,
    cooldown_minutes: int = 0,
) -> ControllableEquipment:
    """Create a test equipment instance (not persisted)."""
    tenant_id = uuid.uuid4()
    return ControllableEquipment(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tent_id=None,
        name=name,
        equipment_type="relay",
        protocol=protocol,
        protocol_config={"mqtt_topic": f"test_{uuid.uuid4().hex[:6]}"},
        capabilities=["on_off"],
        requested_state={"is_on": False},
        confirmed_state={},
        max_on_minutes=max_on_minutes,
        cooldown_minutes=cooldown_minutes,
        conflicts_with=[],
        enabled=True,
    )
