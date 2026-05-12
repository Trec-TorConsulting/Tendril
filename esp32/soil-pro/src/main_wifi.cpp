/// @file main_wifi.cpp
/// Tendril Soil Pro — WiFi + MQTT firmware.

#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "sensors.h"
#include "tendril_mqtt.h"
#include "tendril_power.h"

static tendril::Power power(BATTERY_ADC_PIN, BATTERY_R1, BATTERY_R2);
static tendril::Mqtt  mqtt(MQTT_HOST, MQTT_PORT, MQTT_DEVICE_ID, MQTT_PSK, TENANT_ID, MQTT_USE_TLS);

static bool wifiConnect() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("[wifi] Connecting");
    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > WIFI_TIMEOUT_MS) { Serial.println(" TIMEOUT"); return false; }
        delay(250); Serial.print(".");
    }
    Serial.printf(" OK (%s)\n", WiFi.localIP().toString().c_str());
    return true;
}

void setup() {
    Serial.begin(115200);
    delay(100);
    Serial.println();
    Serial.println("════════════════════════════════════════");
    Serial.printf( "  Tendril Soil Pro  v%s\n", TENDRIL_FW_VERSION);
    Serial.printf( "  Device: %s  Wake: %s\n", MQTT_DEVICE_ID, tendril::Power::wakeReason());
    Serial.println("════════════════════════════════════════");

    power.begin();
    auto batt = power.read();
    Serial.printf("[power] Battery: %.2fV (%u%%)\n", batt.voltage, batt.percent);
    if (batt.critical) { power.deepSleep(3600); }

    tendril::sensors_begin();

    auto soil    = tendril::sensors_read_soil();
    auto ambient = tendril::sensors_read_ambient();

    // Use soil temp for EC compensation, fallback to ambient
    float solutionTempC = 25.0f;
    if (soil.temp_valid) {
        solutionTempC = (soil.soil_temp_f - 32.0f) * 5.0f / 9.0f;
    } else if (ambient.valid) {
        solutionTempC = (ambient.temp_f - 32.0f) * 5.0f / 9.0f;
    }

    auto runoff = tendril::sensors_read_runoff(solutionTempC);

    Serial.printf("[data] Soil: %d%%, Temp: %.1f°F\n", soil.moisture_pct, soil.soil_temp_f);
    Serial.printf("[data] Runoff pH: %.2f, EC: %.2f mS/cm, PPM: %u\n", runoff.ph, runoff.ec_ms, runoff.ppm);
    if (ambient.valid) {
        Serial.printf("[data] Ambient: %.1f°F, %.1f%% RH\n", ambient.temp_f, ambient.humidity);
    }

    if (!wifiConnect()) { power.deepSleep(SLEEP_SECONDS); }

    mqtt.begin();
    uint32_t t0 = millis();
    while (!mqtt.loop()) {
        if (millis() - t0 > MQTT_TIMEOUT_MS) { power.deepSleep(SLEEP_SECONDS); }
        delay(100);
    }

    char payload[256];
    if (soil.valid) {
        tendril::soil_to_json(soil, payload, sizeof(payload));
        mqtt.publish("readings", payload);
    }
    if (runoff.valid) {
        tendril::runoff_to_json(runoff, payload, sizeof(payload));
        mqtt.publish("runoff", payload);
    }
    if (ambient.valid) {
        tendril::ambient_to_json(ambient, payload, sizeof(payload));
        mqtt.publish("ambient", payload);
    }

    mqtt.heartbeat(batt.voltage, batt.percent);
    if (batt.low) mqtt.publishDiag("Low battery");

    delay(200);
    mqtt.loop();
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    power.deepSleep(SLEEP_SECONDS);
}

void loop() {}
