#pragma once
#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID           "YOUR_SSID"
#define WIFI_PASS           "YOUR_PASSWORD"
#define MQTT_HOST           "emqx.your-domain.com"
#define MQTT_PORT           8883
#define MQTT_USE_TLS        true
#define MQTT_DEVICE_ID      "td-XXXXXXXXXXXX"
#define MQTT_PSK            "YOUR_PRE_SHARED_KEY"
#define TENANT_ID           "your-tenant-uuid"

// ─── Pins (ESP32 defaults, override via build_flags for C6) ──
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
#ifndef MOSFET_PIN
#define MOSFET_PIN          27      // Controls 5V rail (HIGH = on)
#endif
#ifndef BATTERY_ADC_PIN
#define BATTERY_ADC_PIN     35
#endif

// ─── pH Calibration ─────────────────────────────────
#define PH_VOLTAGE_AT_7     1.50f
#define PH_VOLTAGE_AT_4     2.03f

// ─── EC Calibration ─────────────────────────────────
#define EC_K_VALUE          1.0f    // K=1 for DFR0300 (general hydro range)
#define EC_TEMP_COEFF       0.019f

// ─── Water Level ────────────────────────────────────
#define TANK_DEPTH_CM       40      // Sensor-to-bottom when empty
#define TANK_FULL_CM        5       // Sensor-to-water when full

// ─── Timing ─────────────────────────────────────────
#define SLEEP_SECONDS       300
#define WIFI_TIMEOUT_MS     15000
#define MQTT_TIMEOUT_MS     10000
#define PROBE_WARMUP_MS     2000

// ─── Battery ────────────────────────────────────────
#define BATTERY_R1          100000
#define BATTERY_R2          100000

#endif
