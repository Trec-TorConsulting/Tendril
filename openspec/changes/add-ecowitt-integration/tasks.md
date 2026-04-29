## 1. Connector
- [x] 1.1 Create `api/app/integrations/connectors/ecowitt.py`
- [x] 1.2 Implement webhook handler for Ecowitt custom server payload format (imperial → metric conversion)
- [x] 1.3 Implement cloud API polling (api.ecowitt.net/api/v3/device/real_time with metric units)
- [x] 1.4 Map Ecowitt fields: outdoor temp, humidity, soil moisture (ch1-16), soil temp, wind, rain, UV, pressure, dew point, leaf wetness (ch1-8), temp/humidity channels (ch1-8)

## 2. Frontend
- [ ] 2.1 Add Ecowitt option to integration type selector
- [ ] 2.2 Create config form with two modes: webhook (show URL to paste in gateway) and cloud API (API key)
- [ ] 2.3 Show webhook URL and setup instructions for Ecowitt gateway custom server config

## 3. Validation
- [x] 3.1 Unit tests for webhook mode with mocked payloads (23 tests passing)
- [x] 3.2 Unit tests for cloud API polling with mocked responses
- [x] 3.3 Verify soil moisture data flows to BucketSensorReading
- [x] 3.4 Verify weather data maps to WeatherReading with source="ecowitt"
