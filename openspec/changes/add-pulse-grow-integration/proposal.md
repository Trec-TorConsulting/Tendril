# Change: Add Pulse Grow Integration

## Why
Pulse Grow monitors (Pulse One, Pulse Pro, Pulse Hub) are extremely popular in the grow community. They offer a free REST API at `api.pulsegrow.com` providing temperature, humidity, VPD, light intensity, CO2, and dew point data. Many Tendril users likely already own one.

## What Changes
- New Pulse Grow connector in `tendril/api/app/integrations/connectors/pulse.py`
- Polls Pulse API on configurable interval (default 5 min)
- Maps Pulse device readings → TentAmbientReading (temp, humidity) + BucketSensorReading (VPD data)
- Setup UI for entering Pulse API key and mapping devices to tents

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework` (must be built first)
- No breaking changes

## Integration Details
- **API Base**: `https://api.pulsegrow.com`
- **Auth**: API key (header)
- **Endpoints**: Device list, latest readings, historical data
- **Data Fields**: temperature, humidity, vpd, lux, dew_point, co2 (Pro/Hub only)
- **Rate Limits**: Reasonable free tier, polling every 5 min is safe
- **Effort**: LOW — well-documented REST API
