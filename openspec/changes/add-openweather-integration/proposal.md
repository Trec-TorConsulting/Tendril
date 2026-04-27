# Change: Add OpenWeather Integration

## Why
Tendril already has a weather endpoint for outdoor grows but it needs real forecast data. OpenWeather API provides a free tier (1000 calls/day) with current conditions, hourly/daily forecasts, UV index, and precipitation — critical for outdoor and greenhouse growers.

## What Changes
- New OpenWeather connector in `tendril/api/app/integrations/connectors/openweather.py`
- Polls OpenWeather API based on tent GPS coordinates or zip code
- Stores data in existing weather tables
- Enhances outdoor grow AI context with real forecast data
- Frost warnings, rain alerts, UV index recommendations

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- No breaking changes

## Integration Details
- **API Base**: `https://api.openweathermap.org/data/3.0`
- **Auth**: API key (query param)
- **Free Tier**: 1000 calls/day
- **Data**: Current weather, 7-day forecast, UV index, precipitation, wind, humidity
- **Effort**: LOW
