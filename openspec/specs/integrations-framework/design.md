## Context
Tendril needs a unified integration framework to connect third-party grow equipment, sensors, and platforms. Rather than building one-off integrations, we create a shared foundation that all integrations plug into.

## Goals / Non-Goals
- **Goals**: Unified config model, webhook receiver, polling worker, device mapping, credential encryption, sync logging
- **Non-Goals**: Building individual integration connectors (those are separate proposals), real-time streaming (polling/webhook is sufficient)

## Decisions
- **IntegrationConfig stores JSON config**: Each integration type has different fields (API keys, hosts, poll intervals). A typed `config` JSON column keeps the schema flexible without migrations per integration.
- **Fernet encryption for credentials**: Symmetric encryption using a server-side key. Simple, no external KMS dependency. Key stored in environment variable.
- **Webhook secret per integration**: Each integration config gets a unique webhook_secret for inbound authentication. External platforms include this in their POST.
- **Polling via APScheduler**: The existing Tendril scheduler pod already runs APScheduler. Add polling jobs dynamically when integrations are created.
- **Data flows into existing tables**: No new sensor tables. External data maps to BucketSensorReading and TentAmbientReading columns. AI context builder requires zero changes.

## Data Model

```
IntegrationConfig:
  id              UUID PK
  tenant_id       UUID FK → tenants.id (RLS)
  type            VARCHAR(50)   -- pulse, ecowitt, home_assistant, etc.
  name            VARCHAR(255)  -- user-friendly label
  config          JSON          -- encrypted credentials + settings
  webhook_secret  VARCHAR(255)  -- unique secret for inbound webhooks
  enabled         BOOLEAN       -- toggle on/off
  poll_interval_s INTEGER       -- seconds between polls (NULL = webhook-only)
  last_synced_at  DATETIME(tz)
  error_count     INTEGER DEFAULT 0
  created_at      DATETIME(tz)
  updated_at      DATETIME(tz)

IntegrationDeviceMap:
  id              UUID PK
  tenant_id       UUID FK → tenants.id (RLS)
  integration_id  UUID FK → integration_configs.id
  external_id     VARCHAR(255)  -- device ID in external system
  external_name   VARCHAR(255)  -- human label from external system
  tent_id         UUID FK → tents.id (nullable)
  bucket_id       UUID FK → buckets.id (nullable)
  sensor_mapping  JSON          -- field map: {"ext_field": "tendril_column"}
  enabled         BOOLEAN
  created_at      DATETIME(tz)

IntegrationSyncLog:
  id              UUID PK
  tenant_id       UUID FK → tenants.id (RLS)
  integration_id  UUID FK → integration_configs.id
  status          VARCHAR(20)   -- success, error, partial
  readings_count  INTEGER
  error_message   TEXT
  synced_at       DATETIME(tz)
```

## API Endpoints

```
POST   /v1/integrations                  -- Create integration config
GET    /v1/integrations                  -- List all for tenant
GET    /v1/integrations/{id}             -- Get single config
PATCH  /v1/integrations/{id}             -- Update config
DELETE /v1/integrations/{id}             -- Delete config + mappings

POST   /v1/integrations/{id}/devices     -- Create device mapping
GET    /v1/integrations/{id}/devices     -- List device mappings
PATCH  /v1/integrations/{id}/devices/{device_id}  -- Update mapping
DELETE /v1/integrations/{id}/devices/{device_id}  -- Remove mapping

POST   /v1/integrations/webhook/{integration_id}  -- Inbound webhook (no auth header, uses webhook_secret in body/query)

GET    /v1/integrations/{id}/logs        -- Sync history
POST   /v1/integrations/{id}/sync        -- Trigger manual sync
```

## Risks / Trade-offs
- **JSON config flexibility vs type safety**: We lose schema validation at DB level. Mitigated by Pydantic validation per integration type in the API layer.
- **Polling load**: Many integrations polling frequently could strain the scheduler. Mitigated by minimum 60s interval and staggered scheduling.
- **Credential encryption key rotation**: Fernet key is static. Future enhancement: support key rotation without re-encryption downtime.

## Migration Plan
1. Alembic migration `0018_integrations_framework.py` creates all three tables with RLS
2. No data migration needed — additive only
3. Rollback: drop tables (no existing data affected)

## Open Questions
- None — framework is intentionally generic. Integration-specific logic lives in each connector proposal.
