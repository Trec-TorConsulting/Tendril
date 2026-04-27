## 1. Database
- [ ] 1.1 Create Alembic migration `0018_integrations_framework.py` with IntegrationConfig, IntegrationDeviceMap, IntegrationSyncLog tables + RLS policies
- [ ] 1.2 Create SQLAlchemy models in `tendril/api/app/integrations/models.py`

## 2. API
- [ ] 2.1 Create Pydantic schemas for integration CRUD (IntegrationCreate, IntegrationUpdate, IntegrationResponse, DeviceMapCreate, etc.)
- [ ] 2.2 Create routes in `tendril/api/app/integrations/routes.py` — CRUD for configs, device mappings, sync logs
- [ ] 2.3 Create webhook receiver endpoint with webhook_secret validation
- [ ] 2.4 Create manual sync trigger endpoint
- [ ] 2.5 Register integration router in `app/main.py`

## 3. Infrastructure
- [ ] 3.1 Implement Fernet credential encryption/decryption utility in `tendril/api/app/integrations/crypto.py`
- [ ] 3.2 Add INTEGRATION_ENCRYPTION_KEY to environment/config
- [ ] 3.3 Create base connector class in `tendril/api/app/integrations/connectors/base.py` with `poll()` and `handle_webhook()` abstract methods
- [ ] 3.4 Add polling job registration to existing scheduler

## 4. Frontend
- [ ] 4.1 Create integrations settings page at `/dashboard/settings/integrations`
- [ ] 4.2 Create integration config form (type selector, credentials, device mapping)
- [ ] 4.3 Create sync status dashboard showing last sync, error count, log history

## 5. Validation
- [ ] 5.1 Run Alembic migration on dev
- [ ] 5.2 Test CRUD endpoints
- [ ] 5.3 Test webhook receiver with mock payload
- [ ] 5.4 Verify RLS isolates tenant data
