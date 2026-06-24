/// @file main_wifi.cpp
/// Tendril Environment Monitor — WiFi + MQTT firmware.

#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "sensors.h"
#include "tendril_mqtt.h"
#include "tendril_power.h"

static tendril::Power power(BATTERY_ADC_PIN, BATTERY_R1, BATTERY_R2);
#ifndef MQTT_CA_CERT
#define MQTT_CA_CERT ""   // PEM CA cert to verify the broker; "" = insecure TLS (dev only)
#endif
static tendril::Mqtt  mqtt(MQTT_HOST, MQTT_PORT, MQTT_DEVICE_ID, MQTT_PSK, TENANT_ID, MQTT_USE_TLS, MQTT_CA_CERT);

static bool wifiConnect() {
    WiFi.mode(WIFI_STA); WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("[wifi] Connecting");
    uint32_t s = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - s > WIFI_TIMEOUT_MS) { Serial.println(" TIMEOUT"); return false; }
        delay(250); Serial.print(".");
    }
    Serial.printf(" OK (%s)\n", WiFi.localIP().toString().c_str());
    return true;
}

void setup() {
    Serial.begin(115200); delay(100);
    Serial.println("\n════════════════════════════════════════");
    Serial.printf("  Tendril Environment Monitor  v%s\n", TENDRIL_FW_VERSION);
    Serial.printf("  Device: %s  Wake: %s\n", MQTT_DEVICE_ID, tendril::Power::wakeReason());
    Serial.println("════════════════════════════════════════");

    power.begin();
    auto batt = power.read();
    Serial.printf("[power] Battery: %.2fV (%u%%)\n", batt.voltage, batt.percent);
    if (batt.critical) power.deepSleep(3600);

    tendril::sensors_begin();
    auto env = tendril::sensors_read_all();

    Serial.printf("[data] Temp: %.1f°F, RH: %.1f%%, VPD: %.2f kPa\n",
                  env.temp_f, env.humidity, env.vpd_kpa);
    Serial.printf("[data] CO₂: %u ppm, Light: %.0f lux, Pressure: %.1f hPa\n",
                  env.co2_ppm, env.lux, env.pressure_hpa);

    if (!wifiConnect()) power.deepSleep(SLEEP_SECONDS);
    mqtt.begin();
    uint32_t t0 = millis();
    while (!mqtt.loop()) { if (millis()-t0>MQTT_TIMEOUT_MS) power.deepSleep(SLEEP_SECONDS); delay(100); }

    char payload[400];
    tendril::env_to_json(env, payload, sizeof(payload));
    mqtt.publish("environment", payload);

    mqtt.heartbeat(batt.voltage, batt.percent);
    if (batt.low) mqtt.publishDiag("Low battery");
    delay(200); mqtt.loop();
    WiFi.disconnect(true); WiFi.mode(WIFI_OFF);
    power.deepSleep(SLEEP_SECONDS);
}
void loop() {}
