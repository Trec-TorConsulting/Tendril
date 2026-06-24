#include "tendril_mqtt.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Static instances — PubSubClient needs a persistent client reference.
static WiFiClient       plainClient;
static WiFiClientSecure tlsClient;
static PubSubClient     mqttClient;

namespace tendril {

Mqtt::Mqtt(const char* host, uint16_t port,
           const char* device_id, const char* psk, const char* tenant_id,
           bool use_tls, const char* ca_cert)
    : _host(host), _port(port), _deviceId(device_id),
      _psk(psk), _tenantId(tenant_id), _useTls(use_tls), _caCert(ca_cert)
{}

void Mqtt::_buildTopics() {
    snprintf(_topicBase,   sizeof(_topicBase),   "t/%s/d/%s/sensor", _tenantId, _deviceId);
    snprintf(_statusTopic, sizeof(_statusTopic), "t/%s/d/%s/status", _tenantId, _deviceId);
    snprintf(_diagTopic,   sizeof(_diagTopic),   "t/%s/d/%s/diag",   _tenantId, _deviceId);
}

void Mqtt::begin() {
    _buildTopics();

    if (_useTls) {
        if (_caCert && _caCert[0] != '\0') {
            // Verify the broker against the pinned CA certificate.
            tlsClient.setCACert(_caCert);
            Serial.println("[mqtt] TLS: broker certificate verification ENABLED");
        } else {
            // No CA configured: the link is encrypted but the broker identity is
            // NOT verified, leaving it open to man-in-the-middle attacks. Provide
            // MQTT_CA_CERT in config.h to enable verification for production.
            tlsClient.setInsecure();
            Serial.println("[mqtt] WARNING: TLS certificate verification DISABLED "
                           "(no CA cert) -- set MQTT_CA_CERT for production");
        }
        mqttClient.setClient(tlsClient);
    } else {
        mqttClient.setClient(plainClient);
    }

    mqttClient.setServer(_host, _port);
    mqttClient.setBufferSize(512);
    mqttClient.setKeepAlive(60);
    _state = MqttState::DISCONNECTED;
}

bool Mqtt::_connect() {
    if (mqttClient.connected()) {
        _state = MqttState::CONNECTED;
        return true;
    }

    _state = MqttState::CONNECTING;
    Serial.printf("[mqtt] Connecting to %s:%u as %s ...\n", _host, _port, _deviceId);

    // LWT: broker publishes offline status if we disconnect unexpectedly
    const char* lwt = "{\"status\":\"offline\"}";

    bool ok = mqttClient.connect(
        _deviceId,   // Client ID
        _deviceId,   // Username (device ID)
        _psk,        // Password (PSK)
        _statusTopic, 1, true, lwt
    );

    if (ok) {
        _state = MqttState::CONNECTED;
        _connectAttempts = 0;
        // Announce online
        mqttClient.publish(_statusTopic, "{\"status\":\"online\"}", true);
        Serial.println("[mqtt] Connected");
        return true;
    }

    _connectAttempts++;
    Serial.printf("[mqtt] Connect failed (rc=%d), attempt %u\n",
                  mqttClient.state(), _connectAttempts);
    _state = MqttState::DISCONNECTED;
    return false;
}

bool Mqtt::loop() {
    if (!mqttClient.connected()) {
        if (!_connect()) return false;
    }
    mqttClient.loop();
    return true;
}

bool Mqtt::publish(const char* subtopic, const char* json_payload) {
    if (!mqttClient.connected()) return false;

    char topic[256];
    snprintf(topic, sizeof(topic), "%s/%s", _topicBase, subtopic);

    bool ok = mqttClient.publish(topic, json_payload);
    if (ok) _lastPublishMs = millis();
    return ok;
}

bool Mqtt::heartbeat(float battery_v, uint8_t battery_pct) {
    if (!mqttClient.connected()) return false;

    JsonDocument doc;
    doc["status"]      = "online";
    doc["battery_v"]   = serialized(String(battery_v, 2));
    doc["battery_pct"] = battery_pct;
    doc["uptime_ms"]   = millis();
    doc["rssi"]        = WiFi.RSSI();

    char buf[200];
    serializeJson(doc, buf, sizeof(buf));
    return mqttClient.publish(_statusTopic, buf, true);
}

bool Mqtt::publishDiag(const char* message) {
    if (!mqttClient.connected()) return false;

    JsonDocument doc;
    doc["msg"]  = message;
    doc["ts"]   = millis();
    doc["rssi"] = WiFi.RSSI();

    char buf[256];
    serializeJson(doc, buf, sizeof(buf));
    return mqttClient.publish(_diagTopic, buf);
}

uint32_t Mqtt::secondsSinceLastPublish() const {
    if (_lastPublishMs == 0) return UINT32_MAX;
    return (millis() - _lastPublishMs) / 1000;
}

} // namespace tendril
