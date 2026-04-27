## 1. Connector
- [ ] 1.1 Create `tendril/api/app/integrations/connectors/home_assistant.py`
- [ ] 1.2 Implement `discover_devices()` — fetch all HA entities, filter to sensor/switch/climate types
- [ ] 1.3 Implement `poll()` — fetch mapped entity states and write to sensor tables
- [ ] 1.4 Implement `execute_action(service, data)` — call HA services for automation triggers
- [ ] 1.5 Map HA entity attributes to Tendril sensor columns (temperature, humidity, power, etc.)

## 2. Frontend
- [ ] 2.1 Add Home Assistant option to integration type selector
- [ ] 2.2 Create HA config form (host URL, access token, test connection button)
- [ ] 2.3 Create entity browser that shows all HA entities with type filtering
- [ ] 2.4 Create entity-to-tent/bucket mapping UI
- [ ] 2.5 Add HA action selector to automation rule actions (e.g., "Turn on HA switch")

## 3. Validation
- [ ] 3.1 Test with real HA instance at 192.168.4.20
- [ ] 3.2 Verify sensor data flows from HA → Tendril → AI context
- [ ] 3.3 Verify automation can trigger HA services
- [ ] 3.4 Test entity discovery with various HA device types
