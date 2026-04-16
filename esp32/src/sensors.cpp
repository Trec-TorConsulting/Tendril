#include "sensors.h"
#include "mqtt_client.h"
#include <ArduinoJson.h>

// Placeholder sensor reads — replace with actual I2C/analog reads per kit type

void sensors_setup() {
    // TODO: Initialize I2C bus, ADC channels for pH/EC/temp probes
    Serial.println("Sensors initialized");
}

void sensors_read_and_publish() {
    JsonDocument doc;

    // Simulated readings — replace with real sensor reads
    doc["water_temp_f"] = 68.5;
    doc["ph"] = 5.9;
    doc["ec"] = 1.2;
    doc["water_level_pct"] = 85;
    doc["ambient_temp_f"] = 75.2;
    doc["ambient_humidity"] = 55.0;

    char payload[256];
    serializeJson(doc, payload, sizeof(payload));

    mqtt_publish("readings", payload);
    Serial.print("Published: ");
    Serial.println(payload);
}
