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

#ifndef I2C_SDA
#define I2C_SDA             21
#endif
#ifndef I2C_SCL
#define I2C_SCL             22
#endif
#ifndef BATTERY_ADC_PIN
#define BATTERY_ADC_PIN     35
#endif

// ─── SCD41 CO₂ Compensation ────────────────────────
#define ALTITUDE_M          0       // Your altitude in metres (for pressure compensation)

// ─── Timing ─────────────────────────────────────────
#define SLEEP_SECONDS       300
#define WIFI_TIMEOUT_MS     15000
#define MQTT_TIMEOUT_MS     10000
#define CO2_MEASUREMENT_MS  5500    // SCD41 needs ~5 s per measurement

// ─── Battery ────────────────────────────────────────
#define BATTERY_R1          100000
#define BATTERY_R2          100000

#endif
