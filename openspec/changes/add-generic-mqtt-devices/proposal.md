# Change: Add Generic MQTT Device Support

## Why
Many growers use Tasmota-flashed smart plugs, Shelly relays, and custom MQTT sensors. Tendril already has EMQX but only accepts data from registered Tendril ESP32 devices. Adding configurable generic MQTT device support lets users connect any MQTT-speaking device with a custom topic/payload mapping.

## What Changes
- New generic MQTT connector in `tendril/api/app/integrations/connectors/mqtt_generic.py`
- User configures: external MQTT topic pattern, JSON payload field mapping, target tent/bucket
- MQTT worker subscribes to additional topics for generic devices
- Supports both external broker bridging and direct EMQX publishing

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- Modifies MQTT worker subscription list (additive)
- No breaking changes

## Devices Supported
- Tasmota-flashed smart plugs (power monitoring: watts, kWh)
- Shelly relays (on/off state, power, temperature)
- Custom Arduino/ESP sensors publishing arbitrary JSON
- Any device speaking MQTT with JSON payloads
