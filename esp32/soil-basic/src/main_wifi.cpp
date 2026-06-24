/// @file main_wifi.cpp
/// Tendril Soil Basic — WiFi + MQTT firmware (Arduino framework).
/// Deep-sleep between readings for battery longevity.

#include <Arduino.h>
#include <WiFi.h>

#include "config.h"
#include "sensors.h"
#include "tendril_mqtt.h"
#include "tendril_power.h"

static tendril::Power  power(BATTERY_ADC_PIN, BATTERY_R1, BATTERY_R2);
#ifndef MQTT_CA_CERT
#define MQTT_CA_CERT ""   // PEM CA cert to verify the broker; "" = insecure TLS (dev only)
#endif
static tendril::Mqtt   mqtt(MQTT_HOST, MQTT_PORT, MQTT_DEVICE_ID, MQTT_PSK, TENANT_ID, MQTT_USE_TLS, MQTT_CA_CERT);

// ─── WiFi ──────────────────────────────────────────────
static bool wifiConnect() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("[wifi] Connecting");

    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > WIFI_TIMEOUT_MS) {
            Serial.println(" TIMEOUT");
            return false;
        }
        delay(250);
        Serial.print(".");
    }
    Serial.printf(" OK (%s, RSSI %d)\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
    return true;
}

// ─── Main ──────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    delay(100);

    Serial.println();
    Serial.println("════════════════════════════════════════");
    Serial.printf( "  Tendril Soil Basic  v%s\n", TENDRIL_FW_VERSION);
    Serial.printf( "  Board: %s  Device: %s\n", TENDRIL_BOARD, MQTT_DEVICE_ID);
    Serial.printf( "  Wake reason: %s\n", tendril::Power::wakeReason());
    Serial.println("════════════════════════════════════════");

    // ── Power ──
    power.begin();
    auto batt = power.read();
    Serial.printf("[power] Battery: %.2fV (%u%%)\n", batt.voltage, batt.percent);

    if (batt.critical) {
        Serial.println("[power] CRITICAL battery — sleeping indefinitely until charged");
        power.deepSleep(3600);  // Wake in 1 hour to recheck
    }

    // ── Sensors ──
    bool bmeOk = tendril::sensors_begin();

    // ── Read sensors ──
    auto soil    = tendril::sensors_read_soil();
    auto ambient = tendril::sensors_read_ambient();

    Serial.printf("[data] Soil: %d%% (raw=%d)\n", soil.moisture_pct, soil.raw_adc);
    if (ambient.valid) {
        Serial.printf("[data] Ambient: %.1f°F, %.1f%% RH, %.1f hPa, %.1f kΩ\n",
                      ambient.temp_f, ambient.humidity, ambient.pressure_hpa, ambient.gas_kohms);
    }

    // ── WiFi ──
    if (!wifiConnect()) {
        Serial.println("[wifi] Failed — will retry next wake cycle");
        power.deepSleep(SLEEP_SECONDS);
    }

    // ── MQTT ──
    mqtt.begin();

    uint32_t mqttStart = millis();
    while (!mqtt.loop()) {
        if (millis() - mqttStart > MQTT_TIMEOUT_MS) {
            Serial.println("[mqtt] Connection timeout — sleeping");
            power.deepSleep(SLEEP_SECONDS);
        }
        delay(100);
    }

    // ── Publish ──
    char payload[256];

    if (soil.valid) {
        tendril::soil_to_json(soil, payload, sizeof(payload));
        mqtt.publish("readings", payload);
        Serial.println("[mqtt] Published soil reading");
    }

    if (ambient.valid) {
        tendril::ambient_to_json(ambient, payload, sizeof(payload));
        mqtt.publish("ambient", payload);
        Serial.println("[mqtt] Published ambient reading");
    }

    // Heartbeat with battery status
    mqtt.heartbeat(batt.voltage, batt.percent);

    if (batt.low) {
        mqtt.publishDiag("Low battery warning");
    }

    // Brief delay to let MQTT packets flush
    delay(200);
    mqtt.loop();

    // ── Sleep ──
    Serial.printf("[power] Sleeping for %d seconds\n", SLEEP_SECONDS);
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    power.deepSleep(SLEEP_SECONDS);
}

void loop() {
    // Never reached — deep sleep resets the MCU, re-entering setup().
}
