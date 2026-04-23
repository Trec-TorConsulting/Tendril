#ifndef CONFIG_H
#define CONFIG_H

// ─── WiFi ─────────────────────────────────────────────
#define WIFI_SSID "YOUR_SSID"
#define WIFI_PASS "YOUR_PASSWORD"

// ─── MQTT ─────────────────────────────────────────────
#define MQTT_HOST "emqx.your-domain.com"
#define MQTT_PORT 8883
#define MQTT_DEVICE_ID "td-XXXXXXXXXXXX"
#define MQTT_PSK "YOUR_PRE_SHARED_KEY"

// Tenant (set during provisioning / pairing)
#define TENANT_ID "your-tenant-uuid"

// ─── Pin Assignments (Standard ESP32-WROOM-32) ───────
// I2C — BME680 (default address 0x77)
#define I2C_SDA 21
#define I2C_SCL 22

// Capacitive soil moisture sensors — ADC1 pins (safe with WiFi)
#define SOIL_SENSOR_1_PIN 34   // Bucket/pot 1
#define SOIL_SENSOR_2_PIN 35   // Bucket/pot 2

// ─── Soil Calibration ─────────────────────────────────
// Measure these with YOUR sensors:
//   DRY_VALUE  = analogRead() when sensor is in open air
//   WET_VALUE  = analogRead() when sensor is in a glass of water
// Typical capacitive sensor ranges (12-bit ADC: 0-4095):
#define SOIL_1_DRY_VALUE 2800
#define SOIL_1_WET_VALUE 1200
#define SOIL_2_DRY_VALUE 2800
#define SOIL_2_WET_VALUE 1200

// ─── Intervals ────────────────────────────────────────
// Sensor polling interval (ms) — how often to read + publish
#define SENSOR_POLL_MS 30000

// Heartbeat interval (ms) — device publishes status/online
#define HEARTBEAT_MS 60000

#endif
