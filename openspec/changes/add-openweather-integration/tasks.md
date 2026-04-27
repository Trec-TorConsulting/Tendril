## 1. Connector
- [ ] 1.1 Create `tendril/api/app/integrations/connectors/openweather.py`
- [ ] 1.2 Implement `poll()` — fetch current + forecast for configured location
- [ ] 1.3 Map OpenWeather fields to existing weather data model
- [ ] 1.4 Generate frost warnings and UV alerts as automation triggers

## 2. Frontend
- [ ] 2.1 Add OpenWeather option to integration type selector
- [ ] 2.2 Create config form (API key, location by zip/GPS)
- [ ] 2.3 Display 7-day forecast on grow overview for outdoor grows

## 3. Validation
- [ ] 3.1 Test with real OpenWeather API key
- [ ] 3.2 Verify weather data appears in AI context for outdoor grows
- [ ] 3.3 Verify frost/UV alerts trigger correctly
