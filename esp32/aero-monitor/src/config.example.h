#pragma once
#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID           "YOUR_SSID"
#define WIFI_PASS           "YOUR_PASSWORD"
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

// ─── Pins (ESP32 defaults) ──────────────────────────
#ifndef ONEWIRE_PIN
#define ONEWIRE_PIN         4
#endif
#ifndef PH_ADC_PIN
#define PH_ADC_PIN          32
#endif
#ifndef EC_ADC_PIN
#define EC_ADC_PIN          33
#endif
#ifndef ULTRA_TRIG_PIN
#define ULTRA_TRIG_PIN      25
#endif
#ifndef ULTRA_ECHO_PIN
#define ULTRA_ECHO_PIN      26
#endif
#ifndef PRESSURE_ADC_PIN
#define PRESSURE_ADC_PIN    36
#endif
#ifndef MOSFET_PIN
#define MOSFET_PIN          27
#endif
#ifndef BATTERY_ADC_PIN
#define BATTERY_ADC_PIN     35
#endif

// ─── Calibration ────────────────────────────────────
#define PH_VOLTAGE_AT_7     1.50f
#define PH_VOLTAGE_AT_4     2.03f
#define EC_K_VALUE          1.0f
#define EC_TEMP_COEFF       0.019f

// ─── Water Level ────────────────────────────────────
#define TANK_DEPTH_CM       40
#define TANK_FULL_CM        5

// ─── Pressure Transducer ────────────────────────────
#define PRESSURE_MAX_PSI    150.0f
#define PRESSURE_V_MIN      0.5f
#define PRESSURE_V_MAX      4.5f
#define PRESSURE_R1         47000   // Voltage divider for 4.5V→3.3V
#define PRESSURE_R2         100000

// ─── Timing ─────────────────────────────────────────
#define SLEEP_SECONDS       300
#define WIFI_TIMEOUT_MS     15000
#define MQTT_TIMEOUT_MS     10000
#define PROBE_WARMUP_MS     2000

#define BATTERY_R1          100000
#define BATTERY_R2          100000

#endif
