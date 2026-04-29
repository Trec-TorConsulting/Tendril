# Integrations Framework

The integrations framework provides a unified system for connecting third-party devices, platforms, and services to Tendril. All integrations flow data into existing sensor tables and leverage existing AI context — no changes to the AI pipeline required.

## Architecture

- **IntegrationConfig** table stores per-tenant integration credentials and device mappings
- **IntegrationDeviceMap** table maps external devices/sensors to Tendril tents and buckets
- **IntegrationSyncLog** table tracks sync history and errors
- Webhook receiver endpoint accepts push-style data from external platforms
- Polling workers pull data from cloud APIs on configurable intervals
- **BaseConnector** ABC with registry pattern: `poll()`, `handle_webhook()`, `persist_readings()`, `discover_devices()`
- Connector auto-registration via `@register_connector` decorator
- All sensor data flows into existing `BucketSensorReading`, `TentSensorReading`, and `WeatherReading` tables
- Multi-tenant isolation via RLS on all integration tables
- Fernet symmetric encryption for credentials at rest

## Implemented Connectors

| Connector | Type | Mode | Sensor Tables |
|-----------|------|------|---------------|
| **Pulse Grow** | `pulse` | Polling | TentSensorReading (ambient), BucketSensorReading (Hub sensors) |
| **OpenWeather** | `openweather` | Polling | WeatherReading (current + forecast) |
| **Ecowitt** | `ecowitt` | Webhook + Polling | WeatherReading, BucketSensorReading (soil), TentSensorReading (temp/humidity) |
| **Open-Meteo** | Built-in (scheduler) | Polling | WeatherReading (free baseline, no integration config needed) |

### Requirement: Integration Configuration Management
The system SHALL allow tenants to create, update, list, and delete integration configurations via REST API.

#### Scenario: Create integration config
- **WHEN** a tenant POSTs to `/v1/integrations` with type, credentials, and device mappings
- **THEN** the system stores the encrypted credentials and returns the config without secrets

#### Scenario: List integration configs
- **WHEN** a tenant GETs `/v1/integrations`
- **THEN** the system returns all configs for that tenant with secrets redacted

#### Scenario: Delete integration config
- **WHEN** a tenant DELETEs `/v1/integrations/{id}`
- **THEN** the system removes the config and stops syncing that integration

### Requirement: Webhook Receiver
The system SHALL provide a webhook endpoint that accepts push-style sensor data from external platforms and maps it to existing sensor tables.

#### Scenario: Valid webhook data received
- **WHEN** an external platform POSTs to `/v1/integrations/webhook/{integration_id}`
- **THEN** the system validates the payload, maps fields to sensor columns, and inserts a reading
- **AND** updates the IntegrationSyncLog with success status

#### Scenario: Invalid webhook data
- **WHEN** a webhook POST contains invalid or unmappable data
- **THEN** the system returns 400 and logs the error in IntegrationSyncLog

#### Scenario: Webhook authentication
- **WHEN** a webhook POST does not include a valid webhook secret
- **THEN** the system returns 401

### Requirement: Polling Sync Worker
The system SHALL run background polling tasks for cloud-API-based integrations on configurable intervals.

#### Scenario: Scheduled poll executes
- **WHEN** a polling interval elapses for an enabled integration
- **THEN** the system fetches latest data from the external API, persists sensor readings to the appropriate tables via `connector.persist_readings()`, and logs the sync in IntegrationSyncLog

#### Scenario: Poll failure handling
- **WHEN** a poll fails due to network or API error
- **THEN** the system logs the error in IntegrationSyncLog and retries on next interval
- **AND** does NOT disable the integration automatically

### Requirement: Device Mapping
The system SHALL map external devices/sensors to Tendril tents and buckets, so data flows into the correct context for AI analysis.

#### Scenario: Map external device to tent
- **WHEN** a tenant configures a device mapping with tent_id
- **THEN** ambient sensor data from that device is stored as TentAmbientReading for that tent

#### Scenario: Map external device to bucket
- **WHEN** a tenant configures a device mapping with bucket_id
- **THEN** sensor data from that device is stored as BucketSensorReading for that bucket

### Requirement: Integration Sync Logging
The system SHALL log every sync attempt (success or failure) for observability and debugging.

#### Scenario: Successful sync logged
- **WHEN** a sync completes successfully
- **THEN** a log entry is created with status=success, reading_count, and timestamp

#### Scenario: Failed sync logged
- **WHEN** a sync fails
- **THEN** a log entry is created with status=error, error_message, and timestamp

### Requirement: Credential Security
The system SHALL encrypt integration credentials at rest and never expose raw secrets in API responses.

#### Scenario: Credentials stored encrypted
- **WHEN** a tenant creates an integration with API keys or tokens
- **THEN** the credentials are encrypted before storage using Fernet symmetric encryption

#### Scenario: Credentials redacted in responses
- **WHEN** a tenant retrieves their integration config
- **THEN** credential fields show masked values (e.g., `••••••••last4`)
