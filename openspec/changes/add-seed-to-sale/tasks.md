## 1. Database & Models

- [ ] 1.1 Create Alembic migration: `facilities`, `plant_tags`, `packages`, `package_sources`, `inventory_ledger`, `lab_tests`, `transfers`, `transfer_packages`, `destructions`, `compliance_events`, `tenant_compliance_config` tables
- [ ] 1.2 Create Alembic migration: add `plant_tag_id` nullable FK to `buckets`
- [ ] 1.3 Create DB triggers preventing UPDATE/DELETE on `compliance_events`, `inventory_ledger`, `destructions` (where `witness_confirmed_at` IS NOT NULL)
- [ ] 1.4 Write SQLAlchemy models in `api/app/compliance/models.py`
- [ ] 1.5 Add RLS policies for all new tables (tenant_id isolation)
- [ ] 1.6 Seed `tenant_compliance_config` for existing commercial tenants (disabled)

## 2. Module Scaffolding

- [ ] 2.1 Create `api/app/compliance/` package with `__init__.py`
- [ ] 2.2 Create `permissions.py` with compliance domain permissions (facilities, tags, packages, lab_tests, transfers, destructions, events, reports, config)
- [ ] 2.3 Create `schemas.py` with Pydantic models for all entities (include unit conversion display fields)
- [ ] 2.4 Create `routes.py` router aggregator and register in `main.py`
- [ ] 2.5 Gate all compliance routes behind `require_plan("commercial")` + `compliance_enabled` check

## 3. Facilities (Multi-Location)

- [ ] 3.1 Create `facility_routes.py` — CRUD for licensed facilities
- [ ] 3.2 Implement `facility_service.py` — validation, primary facility management
- [ ] 3.3 Enforce: at least one facility required when compliance is enabled
- [ ] 3.4 Link facilities to existing Tents (facility_id on tent, optional)

## 4. Plant Tagging

- [ ] 4.1 Implement `tag_service.py` — dual-mode provisioning (METRC pre-purchased entry + auto-generation), METRC 24-char format validation, assignment
- [ ] 4.2 Create `plant_tag_routes.py` — CRUD, bulk import (METRC purchased batch), assign to bucket, view lineage (mother→clone chain)
- [ ] 4.3 Emit `plant_tagged` compliance event on tag assignment
- [ ] 4.4 Enforce: one active tag per Bucket, no reassignment (void and create new tag on error)
- [ ] 4.5 Support `source_tag_id` for clone lineage tracking
- [ ] 4.6 Tag status lifecycle: `available → active → harvested/destroyed/transferred/voided`

## 5. Package Management

- [ ] 5.1 Implement `package_service.py` — create, split, merge, weight reconciliation, flexible batching (1:1 or combine multiple yields)
- [ ] 5.2 Implement auto-creation hook: when GrowCycle status → `completed`, auto-create Packages (user pre-configures 1:1 or batch)
- [ ] 5.3 Create `package_routes.py` — CRUD, status transitions, inventory view
- [ ] 5.4 Create `package_sources` join table entries linking packages to their source yields + plant tags
- [ ] 5.5 Emit `package_created` compliance event on creation
- [ ] 5.6 Package status gate: cannot transfer until `qc_status = passed` or `exempt`

## 6. Inventory Ledger

- [ ] 6.1 Implement `inventory_service.py` — ledger entries, balance validation, adjustment workflow, unit conversion helpers
- [ ] 6.2 All weight changes go through ledger (create, sample, transfer, destruction, adjustment)
- [ ] 6.3 Enforce `current_weight_g` on Package always matches latest `balance_after_g` in ledger
- [ ] 6.4 Reconciliation endpoint: compare ledger totals vs package weights, flag discrepancies
- [ ] 6.5 Unit conversion: store grams internally, expose `weight_display` in API responses per tenant preference

## 7. Lab Testing

- [ ] 7.1 Create `lab_test_routes.py` — CRUD, status transitions, COA upload
- [ ] 7.2 COA upload via existing `app/storage.py` (S3/MinIO), store key in `coa_storage_key`
- [ ] 7.3 On lab test completion (pass/fail): update Package `qc_status`, emit compliance event
- [ ] 7.4 Create inventory ledger entry for lab sample weight deduction
- [ ] 7.5 Validate: cannot mark package `available` without a passing lab test (unless `qc_status = exempt`)

## 8. Transfers

- [ ] 8.1 Implement `transfer_service.py` — manifest generation, approval workflow, status machine, GPS processing
- [ ] 8.2 Create `transfer_routes.py` — CRUD, add/remove packages, submit for approval, approve/reject, departure, delivery, rejection
- [ ] 8.3 GPS endpoint: `POST /v1/compliance/transfers/{id}/gps` — append point to `gps_log`
- [ ] 8.4 Status transitions: `draft → pending_approval → approved → ready → in_transit → delivered/rejected/cancelled`
- [ ] 8.5 Manager approval endpoint: requires `compliance:transfers:approve` permission
- [ ] 8.6 On delivery: compare `weight_shipped_g` vs `weight_received_g`, create ledger entries
- [ ] 8.7 On departure: deduct from source packages via inventory ledger (`transfer_out`)
- [ ] 8.8 Emit compliance events: `transfer_departed`, `transfer_delivered`, `transfer_rejected`
- [ ] 8.9 Geofence deviation alerting (>1km from planned route → push notification)

## 9. Destruction

- [ ] 9.1 Implement `destruction_service.py` — async witness notification, photo requirement enforcement
- [ ] 9.2 Create `destruction_routes.py` — create destruction, witness confirmation endpoint
- [ ] 9.3 Enforce: `witnessed_by` must be different user from `performed_by`
- [ ] 9.4 Enforce: minimum 1 photo in `photo_storage_keys` (uploaded to S3)
- [ ] 9.5 On creation: send push notification to designated witness
- [ ] 9.6 Witness confirmation deadline (configurable, default 4h) with reminder at 75%
- [ ] 9.7 On witness confirmation: update plant/package status to `destroyed`, create ledger entry
- [ ] 9.8 Emit `destruction_completed` compliance event

## 10. Compliance Event Log

- [ ] 10.1 Create `event_routes.py` — read-only paginated log with filters (entity_type, event_type, date range)
- [ ] 10.2 All services emit events via a shared `emit_compliance_event()` helper
- [ ] 10.3 Events include full entity state snapshot in `payload` JSONB

## 11. Notifications

- [ ] 11.1 Implement `notification_service.py` — multi-channel compliance notifications
- [ ] 11.2 Push notifications via PWA service worker (web push API)
- [ ] 11.3 In-app notification center entries
- [ ] 11.4 Email notifications (compliance-critical events)
- [ ] 11.5 Channel selection configurable per tenant (`notification_channels` in config)
- [ ] 11.6 Event-to-notification mapping: witness requests, approval requests, lab results, sync failures, geofence deviations, deliveries

## 12. Label/QR Generation

- [ ] 12.1 Add `segno` and `python-barcode` to requirements.txt
- [ ] 12.2 Implement `label_generator.py` — QR (SVG/PDF/ZPL) and Code128 barcode generation
- [ ] 12.3 QR encodes `tendril://{tenant_id}/{entity_type}/{tag_number}`
- [ ] 12.4 Endpoint: `GET /v1/compliance/labels/{entity_type}/{id}?format=svg|pdf|zpl`
- [ ] 12.5 Batch label generation for printing sheets (Avery 5160 layout)
- [ ] 12.6 ZPL output for Zebra/Bluetooth thermal printers

## 13. Tenant Configuration

- [ ] 13.1 Create `config_routes.py` — CRUD for `tenant_compliance_config`
- [ ] 13.2 METRC key encryption/decryption (Fernet symmetric, key from env)
- [ ] 13.3 Validate state_code against supported states list
- [ ] 13.4 Enable/disable compliance module per tenant
- [ ] 13.5 Weight unit preference (metric/imperial) configuration
- [ ] 13.6 Transfer approval requirement toggle
- [ ] 13.7 Notification channel selection

## 14. METRC Adapter (NJ-first)

- [ ] 14.1 Implement `metrc_adapter.py` — API client with auth, rate limiting, retry
- [ ] 14.2 Plant endpoints: create plant, change growth phase, destroy plant
- [ ] 14.3 Package endpoints: create package, adjust weight, change status
- [ ] 14.4 Transfer endpoints: create transfer template, update transit status
- [ ] 14.5 Harvest endpoints: create harvest, finish harvest
- [ ] 14.6 Lab test endpoints: record lab test result
- [ ] 14.7 Scheduler job: sync pending `compliance_events` (where `metrc_synced = false`)
- [ ] 14.8 Idempotency: use compliance_event UUID as METRC idempotency key
- [ ] 14.9 Error handling: populate `metrc_error`, trigger notification on failure
- [ ] 14.10 Manual sync trigger endpoint (for review mode)

## 15. AI Assistant Integration

- [ ] 15.1 Create `ai_tools.py` — tool definitions for compliance queries
- [ ] 15.2 Implement `get_compliance_summary` tool — pending items overview
- [ ] 15.3 Implement `query_packages` tool — filter by status, strain, date, weight
- [ ] 15.4 Implement `query_transfers` tool — filter by status, date, destination
- [ ] 15.5 Implement `query_lab_results` tool — filter by package, status, date
- [ ] 15.6 Implement `get_plant_lineage` tool — clone chain from any tag
- [ ] 15.7 Implement `get_inventory_report` tool — current inventory by type/status
- [ ] 15.8 Register tools with AI assistant in `api/app/ai/`

## 16. Tests

- [ ] 16.1 Unit tests: tag provisioning (both modes), weight reconciliation, status machines
- [ ] 16.2 Unit tests: package auto-creation from yields (1:1 and batch)
- [ ] 16.3 Unit tests: destruction witness validation, photo enforcement, async flow
- [ ] 16.4 Unit tests: inventory ledger balance integrity, unit conversion
- [ ] 16.5 Unit tests: METRC adapter request formatting (mocked)
- [ ] 16.6 Unit tests: transfer approval workflow
- [ ] 16.7 Integration tests: full plant → package → transfer → delivery flow
- [ ] 16.8 Integration tests: destruction with async witness confirmation
- [ ] 16.9 Integration tests: compliance event immutability (verify UPDATE/DELETE blocked)
- [ ] 16.10 Integration tests: multi-facility operations

## 17. Web UI

- [ ] 17.1 Compliance settings page (enable/configure, facilities, unit preference, notifications)
- [ ] 17.2 Facilities management page (CRUD licensed locations)
- [ ] 17.3 Plant tags list view + assign/provision tag flow (manual entry + bulk import)
- [ ] 17.4 Packages list view + detail with inventory ledger + source yields
- [ ] 17.5 Lab test entry form + COA upload + results display
- [ ] 17.6 Transfer manifest creation wizard with approval workflow
- [ ] 17.7 Transfer approval inbox for managers
- [ ] 17.8 Destruction form with witness selection + photo upload
- [ ] 17.9 Compliance event log viewer (filterable timeline)
- [ ] 17.10 Label/QR preview + print dialog (PDF + Bluetooth thermal)
- [ ] 17.11 GPS tracking map view for active transfers with geofence visualization
- [ ] 17.12 METRC sync status dashboard (pending/synced/failed events)
- [ ] 17.13 On-demand compliance report generation page
- [ ] 17.14 Compliance notification center integration

## 18. PWA / Mobile

- [ ] 18.1 QR code scanner feature — open camera → detect QR → navigate to entity
- [ ] 18.2 Bluetooth thermal printer pairing + label printing (Web Bluetooth API)
- [ ] 18.3 GPS tracking background mode for drivers during transfers
- [ ] 18.4 Witness confirmation push notification + confirmation screen
- [ ] 18.5 Transfer approval push notification + approve/reject screen
- [ ] 18.6 Mobile-optimized package creation flow (from harvest completion)

## 19. Documentation

- [ ] 19.1 API reference docs for all compliance endpoints
- [ ] 19.2 METRC setup guide (NJ-specific with screenshots)
- [ ] 19.3 Compliance workflow guide (seed → sale walkthrough)
- [ ] 19.4 Multi-facility configuration guide
- [ ] 19.5 Self-hosting notes (no METRC required for non-regulated use)
- [ ] 19.6 Bluetooth printer setup guide (supported models)
