# Change: Add OpenSprinkler Integration

## Why
OpenSprinkler is an open-source irrigation controller with a full local REST API. Perfect for automated watering schedules controlled by Tendril AI based on sensor data and plant stage.

## What Changes
- New OpenSprinkler connector via local REST API
- Reads zone status, run times, rain sensor data
- Can trigger zones and set programs from automation rules
- AI can adjust watering based on soil moisture, weather, and plant stage

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- No breaking changes

## Integration Details
- **API**: Local REST at `http://<ip>:8080/` — fully documented, no auth (password hash in URL)
- **Endpoints**: `/jc` (controller vars), `/js` (station status), `/jp` (programs), `/cm` (run station)
- **Data**: Zone on/off, remaining run time, rain delay, flow sensor readings
- **Hardware**: OpenSprinkler ($150), zones from 8-48 stations
- **Effort**: LOW (fully documented REST API, no auth complexity)
