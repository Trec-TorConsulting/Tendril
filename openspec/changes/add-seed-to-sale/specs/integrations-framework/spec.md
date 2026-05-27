## ADDED Requirements

### Requirement: METRC Compliance Connector
The system SHALL provide a METRC integration connector following the BaseConnector pattern, enabling bidirectional sync between Tendril compliance events and state METRC track-and-trace systems.

The connector SHALL support New Jersey as the primary state, with the architecture supporting additional METRC states (CA, CO, OR, MI, MA) via state-specific configuration.

Unlike other connectors that sync sensor data, the METRC connector syncs compliance events (plant tags, packages, transfers, destructions, lab results) from `compliance_events` to the METRC API.

#### Scenario: Register METRC connector
- **WHEN** the application starts
- **THEN** a `metrc` connector is registered in the integration registry
- **AND** it is available for tenants with compliance enabled and provider set to `metrc`

#### Scenario: Sync compliance events to METRC
- **WHEN** the scheduler worker runs the METRC sync job
- **AND** a tenant has `auto_sync_enabled = true` or a manual sync is triggered
- **THEN** the connector pushes pending `compliance_events` (where `metrc_synced = false`) to the METRC API
- **AND** uses Fernet-decrypted credentials from `tenant_compliance_config`
- **AND** marks events as synced on success or records errors on failure

#### Scenario: METRC credential storage
- **WHEN** a tenant configures METRC integration with API key and vendor key
- **THEN** the system encrypts keys using Fernet symmetric encryption
- **AND** stores them in `tenant_compliance_config`
- **AND** keys are never included in API responses (write-only fields)
