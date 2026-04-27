## ADDED Requirements

### Requirement: Device Registration
The system SHALL allow registering IoT devices with a unique device_id and pre-shared key.

#### Scenario: Register new device
- **WHEN** a device record is created with device_id and PSK
- **THEN** the device is stored with a hashed PSK and status "unpaired"

### Requirement: Device Pairing
The system SHALL allow customers to pair devices to their tenant by scanning a QR code.

#### Scenario: QR code pairing
- **WHEN** a user scans a device QR code in the web app
- **THEN** the system links the device to the user's tenant, assigns it to a tent, and sets status to "paired"

#### Scenario: Already paired device
- **WHEN** a user scans a QR code for a device already paired to another tenant
- **THEN** the system returns an error indicating the device is already claimed

### Requirement: MQTT Device Authentication
The system SHALL authenticate MQTT device connections via EMQX HTTP auth webhook.

#### Scenario: Valid device connect
- **WHEN** an ESP32 connects to EMQX with device_id and PSK
- **THEN** the EMQX webhook validates credentials against the devices table and allows the connection

#### Scenario: Revoked device connect
- **WHEN** a revoked device attempts to connect
- **THEN** the webhook rejects the connection

### Requirement: MQTT Topic Authorization
The system SHALL enforce per-tenant MQTT topic ACLs via EMQX HTTP ACL webhook.

#### Scenario: Device publishes to own topic
- **WHEN** a device publishes to `t/{tenant_id}/d/{device_id}/sensor/ph`
- **THEN** the ACL webhook allows the publish

#### Scenario: Device publishes to another tenant's topic
- **WHEN** a device attempts to publish to a different tenant's topic
- **THEN** the ACL webhook denies the publish

### Requirement: Device Management
The system SHALL provide CRUD operations for devices (list, rename, revoke, delete).

#### Scenario: Revoke device
- **WHEN** a tenant owner revokes a device
- **THEN** the device status is set to "revoked" and subsequent MQTT connections are rejected

### Requirement: Device Status Tracking
The system SHALL track device online/offline status via MQTT last-will and connect events.

#### Scenario: Device goes offline
- **WHEN** a device disconnects unexpectedly
- **THEN** the MQTT last-will message updates the device status to "offline" and records last_seen timestamp
