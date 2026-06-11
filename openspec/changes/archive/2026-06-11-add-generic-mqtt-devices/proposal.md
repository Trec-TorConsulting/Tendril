# Change: Add Generic MQTT Device Support

## Why
Many growers use Tasmota-flashed smart plugs, Shelly relays, custom Arduino/ESP sensors, and other off-the-shelf devices that publish MQTT. Tendril's MQTT worker currently only accepts data from registered Tendril ESP32 devices on the `t/{tenant_id}/d/{device_id}/sensor/#` topic structure. Adding configurable generic MQTT device support lets users connect any MQTT-speaking device by defining a topic subscription and JSON payload field mapping — instantly expanding Tendril's sensor reach without custom firmware.

## What Changes
- New `mqtt_generic` connector in `api/app/integrations/connectors/mqtt_generic.py` following BaseConnector ABC
- Connector processes MQTT messages (not HTTP webhooks) by matching incoming topic against configured device maps
- Uses existing `IntegrationDeviceMap.sensor_mapping` for configurable JSON field mapping (e.g., `{"temperature": "ambient_temp_f"}`)
- MQTT worker subscribes to additional topics defined in mqtt_generic integration configs
- Dynamic subscription management: adds/removes topics when integrations are created/updated/deleted
- Supports flat JSON payloads, nested JSON (dot-notation paths), and numeric string coercion
- New API endpoint to preview/test a topic subscription and show the last received message

## Impact
- Affected specs: `integrations-framework`
- Affected code: `api/app/mqtt/client.py` (additive subscription), new connector file, integration routes (test endpoint)
- **NOT BREAKING**: All existing MQTT device functionality preserved. New subscriptions are additive.
- No schema changes — uses existing `integration_configs` + `integration_device_maps` tables
- Billing: Gated behind existing integration limits

## Devices Supported
- Tasmota-flashed smart plugs (power monitoring: watts, kWh, voltage, current)
- Shelly relays publishing MQTT (on/off state, power, temperature)
- Custom Arduino/ESP32 sensors publishing arbitrary JSON to any topic
- Zigbee2MQTT bridge devices (zigbee sensors via z2m coordinator)
- ESPHome devices publishing via MQTT (native MQTT component)
- Any device speaking MQTT with JSON or numeric payloads
