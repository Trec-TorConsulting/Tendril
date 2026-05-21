## ADDED Requirements
### Requirement: OpenWeather Connector
The system SHALL integrate with the OpenWeather API to provide real weather data and forecasts for outdoor and greenhouse grows.

#### Scenario: Poll current weather
- **WHEN** an OpenWeather integration is enabled and a poll interval elapses
- **THEN** the system fetches current conditions and 7-day forecast and stores them in the weather data model

#### Scenario: Generate weather alerts
- **WHEN** fetched weather data indicates frost risk (temp below 32°F) or extreme UV (index > 8)
- **THEN** the system creates an automation alert for the associated grow
