# Change: Add Ecowitt Integration

## Why
Ecowitt makes affordable weather stations and soil sensors popular with outdoor/greenhouse growers. Their gateways support a "custom server" mode that POSTs data directly to a webhook URL — perfect for Tendril. Also has a cloud REST API for fallback.

## What Changes
- New Ecowitt connector in `tendril/api/app/integrations/connectors/ecowitt.py`
- Webhook receiver mode: Ecowitt gateway pushes data directly to Tendril endpoint
- Cloud API polling mode: fallback for users who can't configure custom server
- Maps Ecowitt sensors to Tendril weather data + soil sensor readings

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- No breaking changes

## Integration Details
- **Webhook Mode**: Ecowitt gateway → `POST /v1/integrations/webhook/{id}` (Ecowitt-specific payload format)
- **Cloud API**: `api.ecowitt.net` (REST, API key auth)
- **Data**: Outdoor temp/humidity, wind, rain, UV, soil moisture, soil temp, barometric pressure
- **Devices**: GW2000 gateway ($30), WH51 soil moisture ($15), WS90 weather station ($120), WFC02 irrigation valve
- **Effort**: LOW-MEDIUM
