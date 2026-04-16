#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "mqtt_client.h"
#include "sensors.h"

void setup() {
    Serial.begin(115200);
    Serial.println("Tendril ESP32 Sensor Hub starting...");

    // Connect WiFi
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");

    mqtt_setup();
    sensors_setup();
}

void loop() {
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
