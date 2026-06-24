#pragma once
/// @file tendril_mqtt.h
/// MQTT client wrapper with Tendril topic conventions, LWT, and TLS-PSK.

#include <Arduino.h>

namespace tendril {

/// Connection state reported to callers.
enum class MqttState : uint8_t {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
};

class Mqtt {
public:
    /// @param host       MQTT broker hostname or IP
    /// @param port       MQTT broker port (8883 for TLS, 1883 for plain)
    /// @param device_id  Unique device ID ("td-XXXXXXXXXXXX")
    /// @param psk        Pre-shared key for authentication
    /// @param tenant_id  Tenant UUID
    /// @param use_tls    Enable TLS-PSK transport (default true for production)
    /// @param ca_cert    PEM-encoded CA certificate used to verify the broker.
    ///                   When null or empty the TLS handshake falls back to
    ///                   INSECURE mode (encrypted but unauthenticated, MITM-able)
    ///                   and a warning is logged. Set this for production.
    Mqtt(const char* host, uint16_t port,
         const char* device_id, const char* psk, const char* tenant_id,
         bool use_tls = true, const char* ca_cert = nullptr);

    /// Initialise the MQTT client.  Call once in setup().
    void begin();

    /// Maintain the connection.  Call in every loop() iteration or after wake.
    /// Returns true if connected and operational.
    bool loop();

    /// Publish a JSON payload to `t/{tenant}/d/{device}/sensor/{subtopic}`.
    bool publish(const char* subtopic, const char* json_payload);

    /// Publish an online heartbeat + battery status.
    bool heartbeat(float battery_v, uint8_t battery_pct);

    /// Publish a diagnostic / error message.
    bool publishDiag(const char* message);

    /// Current state.
    MqttState state() const { return _state; }

    /// Seconds since last successful publish.
    uint32_t secondsSinceLastPublish() const;

private:
    const char* _host;
    uint16_t    _port;
    const char* _deviceId;
    const char* _psk;
    const char* _tenantId;
    bool        _useTls;
    const char* _caCert;

    MqttState   _state = MqttState::DISCONNECTED;
    uint32_t    _lastPublishMs = 0;
    uint8_t     _connectAttempts = 0;

    char _topicBase[128];   // "t/{tenant}/d/{device}/sensor"
    char _statusTopic[128]; // "t/{tenant}/d/{device}/status"
    char _diagTopic[128];   // "t/{tenant}/d/{device}/diag"

    bool _connect();
    void _buildTopics();
};

} // namespace tendril
