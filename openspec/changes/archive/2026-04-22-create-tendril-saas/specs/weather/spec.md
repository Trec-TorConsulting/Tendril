## ADDED Requirements

### Requirement: Weather Data Integration (Open-Meteo)
The system SHALL fetch and cache local weather data from the Open-Meteo API for tents configured as outdoor grows.

#### Scenario: Weather fetch for outdoor tent
- **WHEN** a tent is configured with `environment_type = "outdoor"` and has a location (latitude/longitude)
- **THEN** the scheduler fetches current conditions and 7-day hourly forecast from Open-Meteo every 30 minutes and stores the data linked to the tent and tenant

#### Scenario: Weather variables collected
- **WHEN** weather data is fetched for an outdoor tent
- **THEN** the system stores: temperature, humidity, apparent temperature, VPD (vapour pressure deficit), precipitation, rain probability, UV index, wind speed/gusts, cloud cover, soil temperature (0-18cm), soil moisture, ET₀ evapotranspiration, sunrise/sunset times, and daylight duration

#### Scenario: Weather API failure
- **WHEN** the Open-Meteo API is unreachable or returns an error
- **THEN** the system retries with exponential backoff (30s, 60s, 120s) and continues serving cached data; an alert is created if weather data is stale for more than 2 hours

#### Scenario: Location from browser geolocation
- **WHEN** a user creates or edits a tent with `environment_type = "outdoor"` and does not manually enter coordinates
- **THEN** the frontend prompts for browser geolocation permission and auto-fills latitude/longitude

#### Scenario: Manual location entry
- **WHEN** a user creates or edits an outdoor tent
- **THEN** the user can manually enter a city/zip or latitude/longitude, and the system geocodes it via Open-Meteo's Geocoding API

### Requirement: Weather API Endpoints
The system SHALL provide REST endpoints for accessing weather data scoped to the authenticated tenant.

#### Scenario: Current weather
- **WHEN** a user requests current weather for an outdoor tent
- **THEN** the system returns the latest cached weather snapshot (temperature, humidity, VPD, wind, UV, precipitation, conditions)

#### Scenario: Weather forecast
- **WHEN** a user requests the forecast for an outdoor tent
- **THEN** the system returns hourly forecast data for up to 7 days

#### Scenario: Weather history
- **WHEN** a user requests historical weather for a tent within a date range
- **THEN** the system returns stored weather readings within the tenant's data retention window

### Requirement: Weather in Health Checks
The system SHALL include weather context when performing AI health checks for outdoor grows.

#### Scenario: Health check with weather
- **WHEN** a scheduled or manual health check runs for a tent with `environment_type = "outdoor"`
- **THEN** the AI prompt includes current weather (temp, humidity, VPD, UV, recent rain, wind) alongside sensor data and camera snapshot for more accurate plant health assessment

#### Scenario: Weather-aware health advice
- **WHEN** the AI evaluates an outdoor grow's health
- **THEN** it factors in weather conditions (e.g., "High UV + low humidity = increase watering", "Frost warning tonight = consider cover", "3 days rain forecast = watch for mold")

### Requirement: Weather Alerts
The system SHALL generate alerts based on weather conditions that could impact outdoor grows.

#### Scenario: Frost alert
- **WHEN** the forecast shows temperature dropping below 4°C (39°F) within the next 24 hours for an outdoor tent
- **THEN** the system creates a high-priority alert: "Frost warning: {temp}°C expected at {time}. Consider covering plants"

#### Scenario: Extreme heat alert
- **WHEN** the forecast shows temperature exceeding 38°C (100°F) within the next 24 hours
- **THEN** the system creates a warning alert: "Extreme heat: {temp}°C expected. Consider shade and extra watering"

#### Scenario: Heavy rain alert
- **WHEN** the forecast shows precipitation exceeding 25mm in the next 12 hours
- **THEN** the system creates an alert: "Heavy rain expected ({amount}mm). Check drainage and watch for overwatering"

#### Scenario: High wind alert
- **WHEN** the forecast shows wind gusts exceeding 50 km/h (31 mph) within the next 24 hours
- **THEN** the system creates an alert: "High winds expected ({speed} km/h gusts). Secure plants and supports"

#### Scenario: High UV alert
- **WHEN** the current or forecast UV index exceeds 8 (very high)
- **THEN** the system creates an informational alert: "UV index very high ({uv}). Monitor for leaf burn on sensitive strains"
