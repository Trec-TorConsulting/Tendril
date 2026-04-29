## 1. Connector
- [x] 1.1 Create `api/app/integrations/connectors/openweather.py`
- [x] 1.2 Implement `poll()` — fetch current + forecast for configured location (2.5 free + 3.0 One Call)
- [x] 1.3 Map OpenWeather fields to WeatherReading model (temp, humidity, wind, UV, precipitation, dew point, pressure)
- [ ] 1.4 Generate frost warnings and UV alerts as automation triggers

## 2. Frontend
- [ ] 2.1 Add OpenWeather option to integration type selector
- [ ] 2.2 Create config form (API key, location by zip/GPS)
- [ ] 2.3 Display 7-day forecast on grow overview for outdoor grows

## 3. Validation
- [x] 3.1 Unit tests with mocked OpenWeather API responses (20 tests passing)
- [ ] 3.2 Verify weather data appears in AI context for outdoor grows
- [ ] 3.3 Verify frost/UV alerts trigger correctly
