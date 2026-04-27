## 1. Connector
- [ ] 1.1 Create `tendril/api/app/integrations/connectors/pulse.py` implementing base connector
- [ ] 1.2 Implement `discover_devices()` — fetch device list from Pulse API
- [ ] 1.3 Implement `poll()` — fetch latest readings and map to sensor tables
- [ ] 1.4 Map Pulse fields: temperature→ambient_temp_f, humidity→ambient_humidity, lux→light data

## 2. Frontend
- [ ] 2.1 Add Pulse Grow option to integration type selector
- [ ] 2.2 Create Pulse-specific config form (API key input, link to Pulse API key docs)
- [ ] 2.3 Add auto-discover button that fetches devices and lets user map to tents

## 3. Validation
- [ ] 3.1 Test with real Pulse API key
- [ ] 3.2 Verify data appears in tent ambient readings
- [ ] 3.3 Verify AI context includes Pulse-sourced data
