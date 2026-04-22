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

    // Bucket-level readings (per-bucket sensors)
    doc["water_temp_f"] = 68.5;
    doc["ph"] = 5.9;
    doc["ec"] = 1.2;
    doc["water_level_pct"] = 85;

    char payload[256];
    serializeJson(doc, payload, sizeof(payload));

    mqtt_publish("readings", payload);
    Serial.print("Published bucket: ");
    Serial.println(payload);

    // Tent-level ambient readings (shared across all buckets in tent)
    JsonDocument ambient;
    ambient["ambient_temp_f"] = 75.2;
    ambient["ambient_humidity"] = 55.0;

    char ambient_payload[128];
    serializeJson(ambient, ambient_payload, sizeof(ambient_payload));

    mqtt_publish("ambient", ambient_payload);
    Serial.print("Published ambient: ");
    Serial.println(ambient_payload);
}
