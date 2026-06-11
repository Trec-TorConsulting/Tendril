# Change: Add Home Assistant Bridge

## Why
Home Assistant (HA) is the most popular home automation platform with 2000+ device integrations. By bridging Tendril to HA, we instantly unlock data from AC Infinity controllers, TrolMaster, Tuya smart plugs, Govee, SwitchBot, and every Zigbee/Z-Wave/WiFi device HA already supports. Bi-directional: Tendril reads sensor states AND can trigger HA services (turn on fan, trigger outlet).

## What Changes
- New HA connector in `tendril/api/app/integrations/connectors/home_assistant.py`
- Polls HA REST API for entity states (temperature sensors, humidity, smart plugs, etc.)
- Can call HA services from Tendril automation rules (e.g., turn on exhaust fan)
- Maps HA entities to Tendril tents/buckets
- WebSocket option for real-time state changes (future enhancement)

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- No breaking changes

## Integration Details
- **API Base**: `http://<HA_HOST>:8123/api/` (local network)
- **Auth**: Long-lived access token (Bearer header)
- **Read**: `GET /api/states` (all entities), `GET /api/states/{entity_id}` (single)
- **Write**: `POST /api/services/{domain}/{service}` (trigger actions)
- **Data**: Any HA entity — temperature, humidity, switch state, power consumption, etc.
- **Effort**: MEDIUM — entity discovery + mapping UI is the main work
