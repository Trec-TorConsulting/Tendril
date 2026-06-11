## 1. Connector
- [ ] 1.1 Create `tendril/api/app/integrations/connectors/opensprinkler.py`
- [ ] 1.2 Implement zone discovery via `/js` endpoint
- [ ] 1.3 Implement zone status polling (on/off, remaining time, flow)
- [ ] 1.4 Implement zone trigger action via `/cm` endpoint
- [ ] 1.5 Read rain sensor and weather data

## 2. Frontend
- [ ] 2.1 Add OpenSprinkler option to integration type selector
- [ ] 2.2 Create config form (device IP, password)
- [ ] 2.3 Show zone status and map zones to tents/grows

## 3. AI Integration
- [ ] 3.1 AI suggests watering adjustments based on soil moisture + weather data
- [ ] 3.2 Include irrigation status in AI context

## 4. Validation
- [ ] 4.1 Test zone discovery and status polling
- [ ] 4.2 Test zone trigger from automation rule
