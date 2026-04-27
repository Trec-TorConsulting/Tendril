## 1. Connector
- [ ] 1.1 Create `tendril/api/app/integrations/connectors/ecowitt.py`
- [ ] 1.2 Implement webhook handler for Ecowitt custom server payload format
- [ ] 1.3 Implement cloud API polling fallback
- [ ] 1.4 Map Ecowitt fields: outdoor temp, humidity, soil moisture, soil temp, wind, rain, UV, pressure

## 2. Frontend
- [ ] 2.1 Add Ecowitt option to integration type selector
- [ ] 2.2 Create config form with two modes: webhook (show URL to paste in gateway) and cloud API (API key)
- [ ] 2.3 Show webhook URL and setup instructions for Ecowitt gateway custom server config

## 3. Validation
- [ ] 3.1 Test webhook mode with Ecowitt gateway
- [ ] 3.2 Test cloud API polling
- [ ] 3.3 Verify soil moisture data flows to bucket sensor readings
- [ ] 3.4 Verify weather data enhances AI context for outdoor grows
