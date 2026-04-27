# Change: Add Tuya Smart Device Integration

## Why
Tuya is the platform behind thousands of affordable WiFi smart plugs, sensors, and switches (sold under brands like Gosund, SmartLife, etc.). Popular with growers for monitoring power consumption, controlling timers, and tracking temperature/humidity with cheap sensors.

## What Changes
- New Tuya connector via Tuya OpenAPI (OAuth2 REST)
- Polls device states for smart plugs (power, on/off), sensors (temp, humidity)
- Can toggle devices on/off for automation actions

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- No breaking changes

## Integration Details
- **API**: Tuya OpenAPI (openapi.tuyaus.com), OAuth2 token auth
- **Auth**: Client credentials → access token (expires every 2 hours)
- **Data**: Power consumption (W), on/off state, temperature, humidity
- **Devices**: Smart plugs ($10-15), temp/humidity sensors ($12), power strips ($25)
- **Effort**: MEDIUM (OAuth2 flow, token refresh required)
