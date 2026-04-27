## ADDED Requirements
### Requirement: Integration Configuration Management
The system SHALL allow tenants to create, update, list, and delete integration configurations via REST API.

#### Scenario: Create integration config
- **WHEN** a tenant POSTs to `/v1/integrations` with type, credentials, and device mappings
- **THEN** the system stores the encrypted credentials and returns the config without secrets

#### Scenario: List integration configs
- **WHEN** a tenant GETs `/v1/integrations`
- **THEN** the system returns all configs for that tenant with secrets redacted

### Requirement: Webhook Receiver
The system SHALL provide a webhook endpoint that accepts push-style sensor data from external platforms and maps it to existing sensor tables.

#### Scenario: Valid webhook data received
- **WHEN** an external platform POSTs to `/v1/integrations/webhook/{integration_id}`
- **THEN** the system validates the payload, maps fields to sensor columns, and inserts a reading

#### Scenario: Webhook authentication
- **WHEN** a webhook POST does not include a valid webhook secret
- **THEN** the system returns 401

### Requirement: Polling Sync Worker
The system SHALL run background polling tasks for cloud-API-based integrations on configurable intervals.

#### Scenario: Scheduled poll executes
- **WHEN** a polling interval elapses for an enabled integration
- **THEN** the system fetches latest data from the external API and inserts sensor readings

### Requirement: Device Mapping
The system SHALL map external devices/sensors to Tendril tents and buckets, so data flows into the correct context for AI analysis.

#### Scenario: Map external device to tent
- **WHEN** a tenant configures a device mapping with tent_id
- **THEN** ambient sensor data from that device is stored as TentAmbientReading for that tent

### Requirement: Integration Sync Logging
The system SHALL log every sync attempt for observability and debugging.

#### Scenario: Successful sync logged
- **WHEN** a sync completes successfully
- **THEN** a log entry is created with status=success, reading_count, and timestamp

### Requirement: Credential Security
The system SHALL encrypt integration credentials at rest and never expose raw secrets in API responses.

#### Scenario: Credentials stored encrypted
- **WHEN** a tenant creates an integration with API keys or tokens
- **THEN** the credentials are encrypted before storage using Fernet symmetric encryption
