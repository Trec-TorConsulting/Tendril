# Change: Add Integrations Framework

## Why
Tendril users have existing grow equipment (Pulse monitors, AC Infinity controllers, Ecowitt weather stations, etc.) that generates valuable data. Currently, the only way to get sensor data into Tendril is via custom ESP32 devices over MQTT. We need a unified framework that lets users connect third-party platforms and devices so their data flows into the AI context automatically.

## What Changes
- New `IntegrationConfig` table for storing integration credentials and settings
- New `IntegrationDeviceMap` table for mapping external devices to tents/buckets
- New `IntegrationSyncLog` table for observability
- New REST API at `/v1/integrations` for CRUD operations
- New webhook receiver at `/v1/integrations/webhook/{id}` for push-style data
- Polling worker infrastructure via existing APScheduler
- Fernet encryption for stored credentials
- Alembic migration `0018_integrations_framework.py`

## Impact
- Affected specs: `integrations-framework` (new)
- Affected code: `tendril/api/app/integrations/` (new module), `tendril/api/app/main.py` (router registration), `tendril/api/migrations/` (new migration)
- No changes to existing sensor tables, AI context, or MQTT infrastructure
- No breaking changes
