#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "mqtt_client.h"
#include "sensors.h"

static bool wifiConnect() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting to WiFi");

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 40) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\nWiFi connected — IP: %s\n", WiFi.localIP().toString().c_str());
        return true;
    }

    Serial.println("\nWiFi connection failed!");
    return false;
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n========================================");
    Serial.println("  Tendril Soil Sensor Kit v1");
    Serial.printf("  Device: %s\n", MQTT_DEVICE_ID);
    Serial.println("========================================\n");

    if (!wifiConnect()) {
        Serial.println("Restarting in 10s...");
        delay(10000);
        ESP.restart();
    }

    mqtt_setup();

    bool bmeFound = sensors_setup();
    if (!bmeFound) {
        Serial.println("NOTE: Running without BME680 — only soil moisture will be reported");
    }

    Serial.println("\nSetup complete. Starting sensor loop...\n");
}

void loop() {
    // Reconnect WiFi if dropped
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi lost — reconnecting...");
        if (!wifiConnect()) {
            delay(5000);
            return;
        }
    }

    mqtt_loop();

    static unsigned long last_poll = 0;
    if (millis() - last_poll >= SENSOR_POLL_MS) {
        last_poll = millis();
        sensors_read_and_publish();
    }

    static unsigned long last_heartbeat = 0;
    if (millis() - last_heartbeat >= HEARTBEAT_MS) {
        last_heartbeat = millis();
        mqtt_heartbeat();
    }
}
