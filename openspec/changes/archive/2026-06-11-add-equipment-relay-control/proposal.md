# Change: Add Equipment Relay Control

## Why
The automation engine can detect threshold violations and fire alerts, but cannot actuate physical hardware. Growers need Tendril to automatically control exhaust fans, lights, heaters, humidifiers, and pumps in response to sensor readings. Without relay control, Tendril is a monitoring platform — with it, Tendril becomes a full grow automation controller.

## What Changes
- New `controllable_equipment` table for relay/outlet/dimmer devices with state tracking and protocol configuration
- New `equipment_state_log` table for historical state changes (on/off events, power readings)
- Equipment CRUD API (`/v1/equipment/`) with protocol-agnostic control endpoint
- Control dispatch service abstracting Tasmota (MQTT), Shelly (HTTP), TP-Link Kasa (local UDP), Tuya (cloud API), and generic MQTT protocols
- Safety interlock system: max-on duration, cooldown periods, conflict detection (e.g., heater + AC cannot be on simultaneously)
- Wire automation engine's rule evaluation to dispatch device commands when `action` is a device command type
- MQTT state listener for equipment feedback (Tasmota publishes state changes to `stat/{topic}/RESULT`)
- Equipment schedule execution via existing EnvironmentSchedule model
- Frontend: equipment management page, relay control cards, automation action selector, dashboard equipment status

## Impact
- Affected specs: `integrations-framework`, `environment-monitoring`, `grow-assistant-core`
- Affected code: `api/app/automation/engine.py` (add action dispatch), `api/app/mqtt/handlers.py` (add equipment state topic), new `api/app/equipment/` module, new frontend pages
- **NOT BREAKING**: All existing functionality preserved. The automation engine continues to fire alerts; new action dispatch is additive. Existing device commands model is reused.
- Migration: New tables only — no schema modifications to existing tables
- Billing: Equipment control gated behind Pro+ plans via `require_usage_limit("equipment_devices")`
