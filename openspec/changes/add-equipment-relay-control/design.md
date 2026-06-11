## Context
The automation engine evaluates sensor readings against threshold rules and fires alerts/tasks, but has no mechanism to actuate physical devices. The `DeviceCommand` model and `send_command_from_automation()` already exist but are never called from rule evaluation. This change bridges that gap.

## Goals / Non-Goals
- **Goals:**
  - Protocol-agnostic relay/outlet/dimmer control (Tasmota, Shelly, Kasa, Tuya, generic MQTT)
  - State tracking with optimistic + confirmed state (device reports back)
  - Safety interlocks preventing dangerous combinations and runaway conditions
  - Seamless integration with existing automation rules and environment schedules
  - Power monitoring where hardware supports it (Tasmota energy readings)
  - Audit trail of all state changes with source attribution (user, automation, schedule)

- **Non-Goals:**
  - PID loop control (future enhancement — this is on/off + dimmer only)
  - Custom firmware for relay boards (we use off-the-shelf Tasmota/Shelly)
  - Direct Zigbee/Z-Wave support (route through HA bridge integration instead)
  - Replacing the existing `equipment` JSON field on Tent (that remains for AI context)

## Decisions

### Equipment Model Design
- **Decision:** New `controllable_equipment` table separate from the existing Tent.equipment JSON field
- **Rationale:** The JSON field stores display-only metadata for AI context. Controllable equipment needs state tracking, protocol config, interlock rules, and command history — a proper relational model.
- **Alternatives:** Considered extending the Device model, but relay switches are not ESP32 devices and use different protocols.

### Protocol Adapter Pattern
- **Decision:** Use a simple dispatch dict mapping `protocol` → async handler function, not the full BaseConnector pattern
- **Rationale:** Equipment control is fire-and-forget commands (not periodic polling with reading persistence). The BaseConnector lifecycle (poll/webhook/persist) doesn't fit. Simple typed async functions are clearer.
- **Alternatives:** BaseConnector subclass — rejected as over-abstraction for stateless command dispatch.

### State Tracking
- **Decision:** Optimistic state update on command send, confirmed state on device feedback
- **Rationale:** User sees immediate feedback. If device doesn't confirm within timeout, state reverts to "unknown" and alert fires.
- **State model:** `requested_state` (what we asked for), `confirmed_state` (what device reported), `last_confirmed_at`

### Safety Interlocks
- **Decision:** Declarative interlock rules stored per-equipment with enforcement at command dispatch (not UI-only)
- **Rationale:** Safety must be server-enforced regardless of client. Interlocks prevent: (1) conflicting equipment, (2) max-on exceeded, (3) cooldown violation, (4) rapid cycling.
- **Enforcement:** `validate_interlock()` called before every command dispatch — blocks command and logs violation if failed.

### Automation Integration
- **Decision:** Add `_dispatch_device_action()` in automation engine's rule evaluation loop, called after alert creation when rule.action is a device command type
- **Rationale:** Minimal change to existing evaluation flow. Alert still fires (observability), device command also fires (actuation).

## Data Model

### controllable_equipment
```sql
id              UUID PK (gen_random_uuid())
tenant_id       UUID FK → tenants.id (CASCADE) + RLS
tent_id         UUID FK → tents.id (nullable — equipment may be tent-independent)
name            VARCHAR(255) NOT NULL
equipment_type  VARCHAR(50) NOT NULL  -- 'relay', 'dimmer', 'smart_plug', 'pump', 'fan_controller'
protocol        VARCHAR(30) NOT NULL  -- 'tasmota_mqtt', 'shelly_http', 'tuya_cloud', 'kasa_local', 'generic_mqtt'
protocol_config JSONB NOT NULL        -- protocol-specific: {mqtt_topic, ip_address, device_id, etc.}
capabilities    JSONB NOT NULL DEFAULT '[]'  -- ['on_off', 'dimmer', 'power_monitor', 'energy_meter']
requested_state JSONB DEFAULT '{}'    -- {is_on: bool, brightness?: int}
confirmed_state JSONB DEFAULT '{}'    -- {is_on: bool, brightness?: int, power_w?: float}
last_confirmed_at TIMESTAMPTZ
max_on_minutes  INTEGER               -- safety: auto-off after N minutes (null = unlimited)
cooldown_minutes INTEGER DEFAULT 0    -- safety: min time between on-cycles
conflicts_with  UUID[]                -- safety: IDs of mutually exclusive equipment
enabled         BOOLEAN DEFAULT true
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

### equipment_state_log
```sql
id              UUID PK (gen_random_uuid())
tenant_id       UUID FK → tenants.id (CASCADE) + RLS
equipment_id    UUID FK → controllable_equipment.id (CASCADE)
action          VARCHAR(30) NOT NULL  -- 'on', 'off', 'set_brightness', 'power_reading'
source          VARCHAR(30) NOT NULL  -- 'user', 'automation', 'schedule', 'interlock', 'device_report'
state_before    JSONB
state_after     JSONB
metadata        JSONB                 -- {rule_id, schedule_id, power_w, energy_kwh, etc.}
created_at      TIMESTAMPTZ DEFAULT now()
```

## Protocol Adapters

### Tasmota (MQTT)
- **Command:** Publish `cmnd/{topic}/Power` → `ON`/`OFF`/`TOGGLE`
- **State feedback:** Subscribe `stat/{topic}/RESULT` → `{"POWER":"ON"}`
- **Power monitoring:** Subscribe `tele/{topic}/SENSOR` → `{"ENERGY":{"Power":120}}`
- **Discovery:** LWT topic `tele/{topic}/LWT` → `Online`/`Offline`
- **Config:** `{mqtt_topic: "tasmota_plug_1"}`

### Shelly (HTTP)
- **Command:** `GET http://{ip}/relay/0?turn=on|off`
- **State check:** `GET http://{ip}/status` → `{"relays":[{"ison":true}]}`
- **Power monitoring:** Status includes `power`, `overpower`
- **Gen2 API:** `POST http://{ip}/rpc/Switch.Set` → `{"id":0,"on":true}`
- **Config:** `{ip_address: "192.168.1.100", generation: 1|2, channel: 0}`

### TP-Link Kasa (Local)
- **Command:** Local encrypted UDP on port 9999
- **State check:** Same UDP protocol, `system.get_sysinfo`
- **Config:** `{ip_address: "192.168.1.101"}`

### Tuya (Cloud)
- **Command:** Existing `TuyaConnector.toggle_device()` method
- **Config:** `{integration_id: UUID, external_device_id: "bf3a0e..."}`

### Generic MQTT
- **Command:** Publish to configurable topic with configurable payload
- **State feedback:** Subscribe to configurable state topic, parse with configurable JSONPath
- **Config:** `{command_topic: "home/relay/1/set", state_topic: "home/relay/1/state", on_payload: "ON", off_payload: "OFF"}`

## Risks / Trade-offs
- **Risk:** Equipment goes offline mid-operation → Mitigation: state confirmation timeout (30s), revert to "unknown", alert user
- **Risk:** Rapid cycling damages equipment → Mitigation: cooldown enforcement, max cycle count per hour
- **Risk:** Network partition leaves relay stuck ON → Mitigation: max_on_minutes watchdog in scheduler (checks every 60s)
- **Risk:** User connects equipment to wrong protocol → Mitigation: discovery/test-connection during setup

## Migration Plan
- New migration (0045): creates `controllable_equipment` + `equipment_state_log` tables with RLS
- Additive only — no existing table modifications
- Rollback: `downgrade()` drops both tables cleanly
- No data migration needed (new feature, no existing data to transform)

## Open Questions
- None — all design decisions resolved. Tasmota/Shelly/Kasa protocols are well-documented. Tuya control already exists.
