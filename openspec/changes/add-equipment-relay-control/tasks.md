## 1. Database & Models
- [x] 1.1 Create Alembic migration 0045: `controllable_equipment` + `equipment_state_log` tables with RLS policies
- [x] 1.2 Create SQLAlchemy models (`ControllableEquipment`, `EquipmentStateLog`) in `api/app/equipment/models.py`
- [x] 1.3 Create Pydantic schemas (Create, Update, Response, Command, StateLog) in `api/app/equipment/schemas.py`

## 2. Protocol Adapters
- [x] 2.1 Create protocol dispatch module `api/app/equipment/protocols/__init__.py` with typed dispatch
- [x] 2.2 Implement Tasmota MQTT adapter (`tasmota.py`) — publish cmnd/{topic}/Power
- [x] 2.3 Implement Shelly HTTP adapter (`shelly.py`) — Gen1 + Gen2 REST APIs
- [x] 2.4 Implement Tuya cloud adapter (`tuya.py`) — delegate to existing TuyaConnector.toggle_device()
- [x] 2.5 Implement generic MQTT adapter (`generic_mqtt.py`) — configurable topic/payload
- [x] 2.6 Write unit tests for all protocol adapters (mocked I/O)

## 3. Safety & Interlocks
- [x] 3.1 Create interlock validation module `api/app/equipment/interlocks.py`
- [x] 3.2 Implement max_on_minutes watchdog check (called by scheduler)
- [x] 3.3 Implement cooldown enforcement (reject command if within cooldown window)
- [x] 3.4 Implement conflict detection (block if conflicts_with equipment is active)
- [x] 3.5 Write unit tests for all interlock scenarios (cooldown, max-on, conflicts, rapid cycling)

## 4. Control Service & API Routes
- [x] 4.1 Create control service `api/app/equipment/service.py` — orchestrates validate → dispatch → log
- [x] 4.2 Create CRUD routes `api/app/equipment/routes.py` (list, create, get, update, delete equipment)
- [x] 4.3 Create command route `POST /v1/equipment/{id}/command` — send on/off/toggle/dim/set
- [x] 4.4 Create state history route `GET /v1/equipment/{id}/history`
- [x] 4.5 Create test-connection route `POST /v1/equipment/{id}/test` — verify protocol connectivity
- [x] 4.6 Register router in `api/app/main.py`
- [x] 4.7 Write integration tests for all CRUD operations and command flow

## 5. MQTT State Listener
- [x] 5.1 Add equipment state topic subscriptions to MQTT worker (`stat/+/RESULT`, configurable)
- [x] 5.2 Implement state confirmation handler — update confirmed_state, log state change
- [x] 5.3 Implement power monitoring handler — parse Tasmota SENSOR telemetry
- [x] 5.4 Write unit tests for state message parsing and confirmation flow

## 6. Automation Integration
- [x] 6.1 Add `_dispatch_device_action()` to automation engine — call send_command_from_automation when rule.action is a device command type
- [x] 6.2 Add scheduler watchdog task — check max_on_minutes violations every 60s, auto-off + alert
- [x] 6.3 Wire EnvironmentSchedule execution to equipment control (light on/off at schedule times)
- [x] 6.4 Write integration tests for automation → equipment command flow

## 7. Frontend
- [x] 7.1 Create equipment management page (`/dashboard/equipment/`) — list, add, edit, delete
- [x] 7.2 Create equipment detail/control card — toggle switch, state indicator, power reading, last-changed
- [x] 7.3 Add equipment action selector in automation rule builder UI
- [x] 7.4 Add equipment status summary to dashboard overview
- [x] 7.5 Create equipment schedule UI (link to existing environment schedules)
- [x] 7.6 Write Vitest component tests for equipment cards and forms

## 8. Documentation & QA
- [x] 8.1 Add OpenAPI docstrings to all new endpoints
- [x] 8.2 Run full existing test suite — confirm zero regressions
- [x] 8.3 Run ruff + black + eslint + type checks — confirm zero new issues
- [ ] 8.4 Manual smoke test: Tasmota relay on/off via API
