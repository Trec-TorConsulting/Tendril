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

// ─── Pin Assignments ────────────────────────────────
#ifndef MOSFET_GATE_PIN
#define MOSFET_GATE_PIN     25      // Controls 5V boost converter
#endif
#ifndef TRIG_PIN
#define TRIG_PIN            13
#endif
#ifndef ECHO_PIN
#define ECHO_PIN            12
#endif
#ifndef ONEWIRE_PIN
#define ONEWIRE_PIN         4
#endif
#ifndef FLOW_PIN
#define FLOW_PIN            14
#endif
#ifndef BATTERY_ADC_PIN
#define BATTERY_ADC_PIN     36
#endif

// ─── Tank Geometry ──────────────────────────────────
#define TANK_DEPTH_CM       60      // Total inside depth of tank
#define SENSOR_OFFSET_CM    3       // Distance from sensor face to tank rim
#define TANK_FULL_CM        55      // Water level at "100% full"

// ─── Flow Calibration ───────────────────────────────
#define FLOW_FACTOR         7.5f    // Pulses per second per L/min (YF-S201 datasheet)
#define FLOW_WINDOW_MS      1000    // Pulse counting window

// ─── Timing ─────────────────────────────────────────
#define SLEEP_SECONDS       300
#define WIFI_TIMEOUT_MS     15000
#define MQTT_TIMEOUT_MS     10000
#define POWER_STABILIZE_MS  100     // Wait after enabling 5V rail

// ─── Battery ────────────────────────────────────────
#define BATTERY_R1          100000
#define BATTERY_R2          100000

#endif
