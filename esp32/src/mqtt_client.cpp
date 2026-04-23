#include "mqtt_client.h"
#include "config.h"
#include <PubSubClient.h>
#include <WiFi.h>
#include <ArduinoJson.h>

static WiFiClient espClient;
static PubSubClient mqttClient(espClient);

static char topicBase[128];
static char statusTopic[160];
static char lastWillPayload[] = "{\"status\":\"offline\"}";

void mqtt_setup() {
    snprintf(topicBase, sizeof(topicBase), "t/%s/d/%s/sensor", TENANT_ID, MQTT_DEVICE_ID);
    snprintf(statusTopic, sizeof(statusTopic), "t/%s/d/%s/status", TENANT_ID, MQTT_DEVICE_ID);

    mqttClient.setServer(MQTT_HOST, MQTT_PORT);
    mqttClient.setBufferSize(512);
}

bool mqtt_connect() {
    if (mqttClient.connected()) return true;

    Serial.println("MQTT connecting...");

    // Connect with device_id as client ID, device_id as username, PSK as password
    // Set last-will on the status topic so EMQX publishes offline if we drop
    if (mqttClient.connect(
        MQTT_DEVICE_ID,      // clientId
        MQTT_DEVICE_ID,      // username
        MQTT_PSK,            // password
        statusTopic,         // willTopic
        1,                   // willQos
        true,                // willRetain
        lastWillPayload      // willMessage
    )) {
        Serial.println("MQTT connected");

        // Publish online status
        mqttClient.publish(statusTopic, "{\"status\":\"online\"}", true);
        return true;
    }

    Serial.printf("MQTT connect failed, rc=%d\n", mqttClient.state());
    return false;
}

void mqtt_loop() {
    if (!mqttClient.connected()) {
        if (!mqtt_connect()) {
            delay(5000);
            return;
        }
    }
    mqttClient.loop();
}

void mqtt_publish(const char* subtopic, const char* payload) {
    char topic[256];
    snprintf(topic, sizeof(topic), "%s/%s", topicBase, subtopic);
    mqttClient.publish(topic, payload);
}

void mqtt_heartbeat() {
    if (mqttClient.connected()) {
        mqttClient.publish(statusTopic, "{\"status\":\"online\"}", true);
    }
}
