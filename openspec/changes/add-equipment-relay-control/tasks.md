## 1. Research & Design
- [ ] 1.1 Survey relay control protocols (Tasmota, Shelly, KasaTPLink, Sonoff, generic MQTT)
- [ ] 1.2 Define device capability model: relay (on/off), dimmer (0-100%), timer, power metering
- [ ] 1.3 Design automation rule actions: toggle relay, set dimmer level, schedule on/off

## 2. Backend
- [ ] 2.1 Create `equipment` table (id, tenant_id, name, device_type, protocol, config, state)
- [ ] 2.2 Create `POST /v1/equipment` — register relay/outlet device
- [ ] 2.3 Create `POST /v1/equipment/{id}/command` — send on/off/toggle/dim command
- [ ] 2.4 Create MQTT listener for equipment state updates (Tasmota RESULT topics)
- [ ] 2.5 Add equipment actions to automation rule engine (trigger relay on sensor threshold)
- [ ] 2.6 Add safety interlocks (max-on duration, cooldown period, conflict detection)

## 3. Frontend
- [ ] 3.1 Create equipment management page (list, add, edit, delete devices)
- [ ] 3.2 Create relay control card (toggle switch, status indicator, last-changed timestamp)
- [ ] 3.3 Add equipment actions in automation rule builder (then → turn on/off relay)
- [ ] 3.4 Add equipment status to dashboard environment section
- [ ] 3.5 Add scheduling UI (light timers, exhaust fan schedules)

## 4. Integrations
- [ ] 4.1 Tasmota MQTT adapter (auto-discover via LWT topics)
- [ ] 4.2 Shelly HTTP adapter (Gen1 + Gen2 API)
- [ ] 4.3 TP-Link Kasa adapter (local UDP protocol)
- [ ] 4.4 Generic MQTT relay adapter (configurable topic + payload mapping)
