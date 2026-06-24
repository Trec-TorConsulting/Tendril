#pragma once
// ─── Tendril Soil Basic — Configuration ──────────────────────────
// Copy this file to config.h and fill in your values.
// NEVER commit config.h — it contains secrets.

#ifndef CONFIG_H
#define CONFIG_H

// ─── WiFi (WiFi variant only) ────────────────────────
#define WIFI_SSID           "YOUR_SSID"
#define WIFI_PASS           "YOUR_PASSWORD"

// ─── MQTT Broker ─────────────────────────────────────
#define MQTT_HOST           "emqx.your-domain.com"
#define MQTT_PORT           8883        // 8883 = TLS, 1883 = plain
#define MQTT_USE_TLS        true
// PEM CA certificate used to verify the broker over TLS. Leave empty ("") for
// insecure/dev mode (encrypted but UNVERIFIED). For production, paste the CA
// chain with literal \n line breaks, e.g.:
//   "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n"
#define MQTT_CA_CERT        ""

// ─── Device Identity (from Tendril dashboard) ────────
#define MQTT_DEVICE_ID      "td-XXXXXXXXXXXX"
#define MQTT_PSK            "YOUR_PRE_SHARED_KEY"
#define TENANT_ID           "your-tenant-uuid"

// ─── Pin Assignments — ESP32-WROOM-32E ───────────────
// Override these in platformio.ini build_flags for ESP32-C6
#ifndef I2C_SDA
#define I2C_SDA             21
#endif
#ifndef I2C_SCL
#define I2C_SCL             22
#endif
#ifndef SOIL_SENSOR_PIN
#define SOIL_SENSOR_PIN     34      // ADC1 — safe with WiFi active
#endif
#ifndef BATTERY_ADC_PIN
#define BATTERY_ADC_PIN     35      // ADC1 via 100K/100K divider
#endif
#ifndef LED_PIN
#define LED_PIN             2
#endif
#ifndef BUTTON_PIN
#define BUTTON_PIN          0       // BOOT button doubles as factory reset
#endif

// ─── Soil Calibration ────────────────────────────────
// Run calibration: hold in air (dry) and submerge to line (wet).
#define SOIL_DRY_VALUE      2800
#define SOIL_WET_VALUE      1200

// ─── Timing ──────────────────────────────────────────
#define SLEEP_SECONDS       300     // 5 minutes between readings
#define WIFI_TIMEOUT_MS     15000   // Max time to wait for WiFi
#define MQTT_TIMEOUT_MS     10000   // Max time to wait for MQTT

// ─── Battery ─────────────────────────────────────────
#define BATTERY_R1          100000  // Top resistor (Ω)
#define BATTERY_R2          100000  // Bottom resistor (Ω)

#endif // CONFIG_H
