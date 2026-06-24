#pragma once
#ifndef CONFIG_H
#define CONFIG_H

// ─── WiFi ────────────────────────────────────────────
#define WIFI_SSID           "YOUR_SSID"
#define WIFI_PASS           "YOUR_PASSWORD"

// ─── MQTT ────────────────────────────────────────────
#define MQTT_HOST           "emqx.your-domain.com"
#define MQTT_PORT           8883
#define MQTT_USE_TLS        true
// PEM CA certificate used to verify the broker over TLS. Leave empty ("") for
// insecure/dev mode (encrypted but UNVERIFIED). For production, paste the CA
// chain with literal \n line breaks, e.g.:
//   "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n"
#define MQTT_CA_CERT        ""
#define MQTT_DEVICE_ID      "td-XXXXXXXXXXXX"
#define MQTT_PSK            "YOUR_PRE_SHARED_KEY"
#define TENANT_ID           "your-tenant-uuid"

// ─── Pins (ESP32-WROOM-32E defaults) ─────────────────
#ifndef I2C_SDA
#define I2C_SDA             21
#endif
#ifndef I2C_SCL
#define I2C_SCL             22
#endif
#ifndef SOIL_SENSOR_PIN
#define SOIL_SENSOR_PIN     34
#endif
#ifndef ONEWIRE_PIN
#define ONEWIRE_PIN         4       // DS18B20 data (with 4.7KΩ pull-up)
#endif
#ifndef PH_ADC_PIN
#define PH_ADC_PIN          32      // DFRobot pH analog output
#endif
#ifndef EC_ADC_PIN
#define EC_ADC_PIN          33      // DFRobot EC analog output
#endif
#ifndef BATTERY_ADC_PIN
#define BATTERY_ADC_PIN     35
#endif
#ifndef LED_PIN
#define LED_PIN             2
#endif
#ifndef BUTTON_PIN
#define BUTTON_PIN          0
#endif

// ─── Probe Power Control ────────────────────────────
// GPIO to enable 5V boost converter (HIGH = on).
// Set to -1 if always powered.
#define PROBE_POWER_PIN     25

// ─── Soil Calibration ───────────────────────────────
#define SOIL_DRY_VALUE      2800
#define SOIL_WET_VALUE      1200

// ─── pH Calibration (stored in NVS after serial calibration) ──
#define PH_VOLTAGE_AT_7     1.50f   // Default voltage at pH 7.0
#define PH_VOLTAGE_AT_4     2.03f   // Default voltage at pH 4.0

// ─── EC Calibration ─────────────────────────────────
#define EC_K_VALUE          10.0f   // Cell constant for DFR0300-H
#define EC_TEMP_COEFF       0.019f  // Temperature compensation coefficient

// ─── Timing ─────────────────────────────────────────
#define SLEEP_SECONDS       300
#define WIFI_TIMEOUT_MS     15000
#define MQTT_TIMEOUT_MS     10000
#define PROBE_WARMUP_MS     2000    // Time to stabilise pH/EC after power-on

// ─── Battery ────────────────────────────────────────
#define BATTERY_R1          100000
#define BATTERY_R2          100000

#endif
