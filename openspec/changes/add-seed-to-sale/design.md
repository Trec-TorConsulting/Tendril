## Context

Tendril needs METRC-compatible seed-to-sale compliance tracking for licensed commercial cannabis operators. New Jersey is the primary target state (development location), with the framework designed to support any METRC state (CA, CO, OR, MI, MA). The feature targets medium commercial operations (50-500 plants) and is gated to the Commercial billing tier.

### Stakeholders
- Licensed commercial cultivators (NJ CRC licensees)
- Compliance officers at cultivation facilities
- State regulatory bodies (via METRC API)
- Tendril platform team (maintenance/ops)

### Constraints
- Must remain self-hostable (METRC integration opt-in, not required)
- Individual plant tracking mandated (METRC requires per-plant tags)
- Compliance events must be immutable (regulatory evidence)
- Package auto-creation on cure completion (no manual step)
- GPS tracking on transfers (full manifest requirement)
- Witness + photo for destruction (NJ CRC requirement)
- No breaking change to existing free/pro tier users

## Goals / Non-Goals

### Goals
- Full METRC-compatible plant-to-package-to-sale chain of custody
- Individual plant tagging with QR/barcode generation
- Automated package creation from completed harvests
- Lab testing workflow (manual entry → COA upload → future API)
- GPS-tracked transfer manifests with driver/vehicle/route
- Witnessed destruction with photo evidence
- Immutable compliance event log for regulatory audit
- NJ METRC adapter as first-class integration

### Non-Goals
- BioTrack / Leaf Data adapters (future phases)
- Retail/dispensary POS integration (out of scope — we're cultivation-side)
- Patient/consumer tracking
- Real-time video surveillance integration
- Financial/tax reporting to the state
- Automatic METRC submission without human review (too risky for v1)
- Offline GPS queuing (not needed — post-delivery log is acceptable for NJ CRC)
- Scheduled automated compliance reports (on-demand only for v1)

## Data Model

### New Tables

```
facilities
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── name (VARCHAR) — e.g., "Main Cultivation", "Processing Facility"
├── license_number (VARCHAR) — state-issued license for this location
├── license_type (VARCHAR) — 'cultivator', 'processor', 'microbusiness', 'distributor'
├── address_line1 (VARCHAR)
├── address_line2 (VARCHAR, nullable)
├── city (VARCHAR)
├── state_code (VARCHAR 2)
├── zip_code (VARCHAR 10)
├── lat (DECIMAL 9,6, nullable)
├── lng (DECIMAL 9,6, nullable)
├── is_primary (BOOLEAN, default false)
├── status (ENUM: active, inactive, pending)
├── metrc_facility_id (VARCHAR, nullable)
├── created_at / updated_at
└── RLS: tenant_id

plant_tags
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── facility_id (FK → facilities)
├── bucket_id (FK → buckets, UNIQUE, nullable) — nullable until assigned
├── tag_number (VARCHAR 24, UNIQUE per tenant) — METRC pre-purchased or auto-generated
├── tag_type (ENUM: seed, clone, vegetative, flowering)
├── provisioning_mode (ENUM: metrc_purchased, auto_generated) — how this tag was created
├── assigned_at (TIMESTAMPTZ, nullable) — null if tag is provisioned but unassigned
├── source_tag_id (FK → plant_tags, nullable) — mother/clone lineage
├── metrc_id (VARCHAR, nullable) — external METRC plant ID
├── status (ENUM: available, active, harvested, destroyed, transferred, voided)
├── created_at / updated_at
└── RLS: tenant_id

packages
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── facility_id (FK → facilities)
├── package_tag (VARCHAR 24, UNIQUE per tenant) — METRC package tag
├── lot_number (VARCHAR, generated)
├── source_grow_id (FK → grow_cycles)
├── strain_id (FK → strains)
├── package_type (ENUM: flower, trim, shake, waste, concentrate, edible, other)
├── initial_weight_g (DECIMAL 10,2)
├── current_weight_g (DECIMAL 10,2) — decremented by transfers/samples/destruction
├── unit_count (INTEGER, nullable) — for discrete items
├── harvest_date (DATE)
├── package_date (TIMESTAMPTZ)
├── expiry_date (DATE, nullable)
├── status (ENUM: created, testing, available, on_hold, transferred, destroyed, empty)
├── metrc_id (VARCHAR, nullable)
├── lab_test_id (FK → lab_tests, nullable) — current/latest test
├── qc_status (ENUM: pending, passed, failed, exempt)
├── notes (TEXT, nullable)
├── created_at / updated_at
└── RLS: tenant_id

package_sources (join table — flexible 1:1 or many:1 packaging)
├── id (UUID, PK)
├── package_id (FK → packages)
├── yield_id (FK → yields)
├── plant_tag_id (FK → plant_tags, nullable)
├── weight_contributed_g (DECIMAL 10,2)
└── notes (TEXT, nullable)

inventory_ledger
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── package_id (FK → packages)
├── event_type (ENUM: created, sample, transfer_out, transfer_in, adjustment, destruction, split, merge)
├── weight_delta_g (DECIMAL 10,2) — positive = add, negative = subtract
├── balance_after_g (DECIMAL 10,2) — denormalized for fast reads
├── reference_id (UUID, nullable) — FK to transfer/destruction/lab_test
├── reference_type (VARCHAR) — polymorphic: 'transfer', 'destruction', 'lab_test'
├── performed_by (FK → users)
├── reason (TEXT, nullable)
├── created_at (TIMESTAMPTZ) — immutable, no updated_at
└── RLS: tenant_id

lab_tests
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── package_id (FK → packages)
├── lab_name (VARCHAR)
├── lab_license_number (VARCHAR, nullable)
├── sample_date (DATE)
├── received_date (DATE, nullable)
├── completed_date (DATE, nullable)
├── status (ENUM: submitted, in_progress, completed, failed)
├── result (ENUM: pass, fail, pending)
├── thc_total_pct (DECIMAL 5,2, nullable)
├── cbd_total_pct (DECIMAL 5,2, nullable)
├── terpene_total_pct (DECIMAL 5,2, nullable)
├── terpene_profile (JSONB, nullable) — {myrcene: 1.2, limonene: 0.8, ...}
├── pesticides_pass (BOOLEAN, nullable)
├── heavy_metals_pass (BOOLEAN, nullable)
├── microbials_pass (BOOLEAN, nullable)
├── mycotoxins_pass (BOOLEAN, nullable)
├── residual_solvents_pass (BOOLEAN, nullable)
├── moisture_pct (DECIMAL 5,2, nullable)
├── water_activity (DECIMAL 5,3, nullable)
├── coa_storage_key (VARCHAR, nullable) — S3 key for Certificate of Analysis PDF
├── raw_results (JSONB, nullable) — full lab data for future parsing
├── metrc_id (VARCHAR, nullable)
├── notes (TEXT, nullable)
├── created_at / updated_at
└── RLS: tenant_id

transfers
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── facility_id (FK → facilities) — origin facility
├── manifest_number (VARCHAR, UNIQUE per tenant) — generated
├── transfer_type (ENUM: wholesale, distribution, destruction_facility, lab, internal)
├── status (ENUM: draft, pending_approval, approved, ready, in_transit, delivered, rejected, cancelled)
├── submitted_by (FK → users) — who created the transfer
├── approved_by (FK → users, nullable) — manager who approved
├── approved_at (TIMESTAMPTZ, nullable)
├── rejection_note (TEXT, nullable) — manager rejection reason (for pending_approval → draft)
├── origin_license (VARCHAR) — sender license number
├── origin_name (VARCHAR)
├── origin_address (TEXT)
├── origin_lat (DECIMAL 9,6, nullable)
├── origin_lng (DECIMAL 9,6, nullable)
├── destination_license (VARCHAR)
├── destination_name (VARCHAR)
├── destination_address (TEXT)
├── destination_lat (DECIMAL 9,6, nullable)
├── destination_lng (DECIMAL 9,6, nullable)
├── driver_name (VARCHAR)
├── driver_license_number (VARCHAR)
├── vehicle_make (VARCHAR, nullable)
├── vehicle_model (VARCHAR, nullable)
├── vehicle_plate (VARCHAR)
├── planned_route (JSONB, nullable) — GeoJSON LineString or waypoints
├── departure_at (TIMESTAMPTZ, nullable)
├── arrival_at (TIMESTAMPTZ, nullable)
├── estimated_arrival_at (TIMESTAMPTZ, nullable)
├── gps_tracking_enabled (BOOLEAN, default true)
├── gps_log (JSONB, nullable) — array of {lat, lng, timestamp} points
├── received_by (VARCHAR, nullable) — name of person who accepted
├── received_at (TIMESTAMPTZ, nullable)
├── rejection_reason (TEXT, nullable) — recipient rejection reason
├── metrc_id (VARCHAR, nullable)
├── notes (TEXT, nullable)
├── created_at / updated_at
└── RLS: tenant_id

transfer_packages
├── id (UUID, PK)
├── transfer_id (FK → transfers)
├── package_id (FK → packages)
├── weight_shipped_g (DECIMAL 10,2)
├── weight_received_g (DECIMAL 10,2, nullable) — filled on delivery confirmation
├── unit_count (INTEGER, nullable)
├── condition_on_receipt (ENUM: good, damaged, partial, missing, nullable)
├── notes (TEXT, nullable)
└── no separate RLS (inherits from transfer)

destructions
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── package_id (FK → packages, nullable) — if destroying a package
├── plant_tag_id (FK → plant_tags, nullable) — if destroying a plant
├── destruction_type (ENUM: waste, failed_harvest, contamination, expired, regulatory, voluntary)
├── method (ENUM: composting, incineration, grinding, other)
├── weight_destroyed_g (DECIMAL 10,2)
├── reason (TEXT)
├── performed_by (FK → users)
├── witnessed_by (FK → users) — different user required
├── performed_at (TIMESTAMPTZ)
├── witness_confirmed_at (TIMESTAMPTZ, nullable)
├── photo_storage_keys (JSONB) — array of S3 keys, minimum 1 required
├── metrc_id (VARCHAR, nullable)
├── notes (TEXT, nullable)
├── created_at (TIMESTAMPTZ) — immutable
└── RLS: tenant_id

compliance_events
├── id (UUID, PK)
├── tenant_id (FK → tenants)
├── event_type (VARCHAR) — e.g., 'plant_tagged', 'package_created', 'lab_submitted', 'transfer_departed', 'destruction_completed'
├── entity_type (VARCHAR) — 'plant_tag', 'package', 'transfer', 'destruction', 'lab_test'
├── entity_id (UUID)
├── actor_id (FK → users)
├── payload (JSONB) — full snapshot of entity state at event time
├── metrc_synced (BOOLEAN, default false)
├── metrc_synced_at (TIMESTAMPTZ, nullable)
├── metrc_error (TEXT, nullable)
├── created_at (TIMESTAMPTZ) — immutable, append-only
└── RLS: tenant_id
— NO updated_at, NO soft deletes — this table is append-only

tenant_compliance_config
├── id (UUID, PK)
├── tenant_id (FK → tenants, UNIQUE)
├── compliance_enabled (BOOLEAN, default false)
├── provider (ENUM: none, metrc, manual)
├── state_code (VARCHAR 2, nullable) — 'NJ', 'CA', 'CO', etc.
├── metrc_api_key_encrypted (BYTEA, nullable) — encrypted at rest
├── metrc_vendor_key_encrypted (BYTEA, nullable)
├── metrc_base_url (VARCHAR, nullable) — per-state METRC API endpoint
├── auto_sync_enabled (BOOLEAN, default false) — auto-push to METRC
├── tag_prefix (VARCHAR, nullable) — custom prefix for auto-generated tags
├── weight_unit_preference (ENUM: metric, imperial, default metric) — display preference
├── require_transfer_approval (BOOLEAN, default true) — manager sign-off on transfers
├── notification_channels (JSONB, default '["push","in_app"]') — enabled: push, in_app, email
├── created_at / updated_at
└── RLS: tenant_id
```

### Modified Tables

```
yields (existing)
├── + package_id (FK → packages, nullable) — links harvest to auto-created package

buckets (existing)
├── + plant_tag_id (FK → plant_tags, nullable) — links bucket to its compliance tag
```

## Architecture

### Module Structure

```
api/app/compliance/
├── __init__.py
├── models.py               # All compliance SQLAlchemy models
├── schemas.py              # Pydantic request/response schemas
├── routes.py               # Router aggregator
├── facility_routes.py      # Facility/location CRUD
├── plant_tag_routes.py     # Tag CRUD, provisioning, assignment, lineage
├── package_routes.py       # Package CRUD, inventory, splits/merges
├── lab_test_routes.py      # Lab test CRUD, COA upload
├── transfer_routes.py      # Transfer manifests, approval, GPS, delivery
├── destruction_routes.py   # Destruction workflow with async witness
├── event_routes.py         # Compliance event log (read-only)
├── report_routes.py        # On-demand compliance reports
├── config_routes.py        # Tenant compliance configuration
├── services/
│   ├── __init__.py
│   ├── facility_service.py # Multi-location management
│   ├── tag_service.py      # Tag generation/provisioning, METRC format validation
│   ├── package_service.py  # Auto-creation from yields, flexible batching, weight reconciliation
│   ├── inventory_service.py # Ledger operations, balance checks, unit conversion
│   ├── transfer_service.py # Manifest generation, approval workflow, GPS log processing
│   ├── destruction_service.py # Async witness notification, photo requirements
│   ├── notification_service.py # Push, in-app, email compliance notifications
│   ├── label_generator.py  # QR/barcode SVG/PDF/ZPL generation (Bluetooth thermal)
│   ├── report_service.py   # On-demand report generation
│   └── metrc_adapter.py    # METRC API client (NJ-first)
├── ai_tools.py             # AI assistant tool definitions for compliance queries
└── permissions.py          # Compliance-domain permission definitions
```

### Integration with Existing Systems

1. **GrowCycle completion hook**: When a GrowCycle's status transitions to `completed` (curing done), `package_service.auto_create_packages()` fires. User configures whether to create one Package per Yield (1:1) or combine multiple Yields into a batch package. Creates inventory ledger entries, emits `package_created` compliance events.

2. **Bucket tag assignment**: Plant tags can be assigned to Buckets at any lifecycle point. In METRC mode, user enters pre-purchased tag numbers. In manual mode, system auto-generates tags. Enforced: one active tag per Bucket, tags cannot be reassigned (void and create new).

3. **Integrations framework**: METRC adapter follows existing `BaseConnector` pattern in `api/app/integrations/`. Uses `tenant_compliance_config` for credentials. Background sync via scheduler worker.

4. **Storage (MinIO/S3)**: COA PDFs and destruction photos stored via existing `app/storage.py` service.

5. **Notifications**: Compliance events trigger multi-channel notifications (push, in-app, email) based on `notification_channels` config. Uses existing notification infrastructure in `api/app/notifications/`.

6. **AI Assistant**: New tool definitions in `ai_tools.py` give the grow assistant read access to compliance data. Supports queries like "what packages are ready for transfer?", "show pending lab results", "which plants need tags?".

7. **Transfer approval workflow**: Transfers require manager approval (`compliance:transfers:approve` permission) before dispatch. Status flow: `draft → pending_approval → approved → ready → in_transit → delivered`.

8. **Destruction witness flow**: Async notification-based. Performer logs destruction → witness receives push notification → confirms from their own device within configurable deadline.

9. **Multi-location**: Facilities table tracks licensed locations. Tags, packages, and transfers are all associated with a facility. Supports inter-facility transfers (transfer_type: `internal`).

10. **Permissions**: New permission domain `compliance` with granular permissions:
   - `compliance:facilities:read`, `compliance:facilities:write`
   - `compliance:tags:read`, `compliance:tags:write`
   - `compliance:packages:read`, `compliance:packages:write`
   - `compliance:lab_tests:read`, `compliance:lab_tests:write`
   - `compliance:transfers:read`, `compliance:transfers:write`, `compliance:transfers:approve`
   - `compliance:destructions:read`, `compliance:destructions:write`, `compliance:destructions:witness`
   - `compliance:events:read`
   - `compliance:reports:generate`
   - `compliance:config:read`, `compliance:config:write`

### METRC Integration Design

```
┌─────────────────┐         ┌──────────────────┐        ┌─────────────┐
│  Tendril API    │────────▶│  compliance_events│───────▶│  METRC API  │
│  (user actions) │         │  (append-only log)│        │  (NJ/CA/CO) │
└─────────────────┘         └──────────────────┘        └─────────────┘
                                     │
                            ┌────────┴────────┐
                            │ Scheduler Worker │
                            │ (sync pending    │
                            │  events to METRC)│
                            └─────────────────┘
```

- **Two-phase commit pattern**: Local event created first (always succeeds), METRC sync attempted by background worker. If METRC fails, `metrc_error` is populated and user is notified.
- **No blocking on METRC**: User operations never wait on METRC API response. Compliance events are queued for async push.
- **Manual review mode (v1 default)**: `auto_sync_enabled = false`. User reviews pending events in a compliance dashboard, then triggers sync batch manually. Prevents accidental regulatory submissions.
- **Idempotency**: Each compliance event has a UUID used as idempotency key for METRC calls.

### GPS Transfer Tracking

- Client (mobile PWA) sends GPS coordinates at configurable intervals (default: every 60 seconds) to `POST /v1/compliance/transfers/{id}/gps` during active transit.
- Points stored as JSONB array on the transfer record (simple for v1, PostGIS upgrade path for v2).
- Transfer status transitions: `draft → pending_approval → approved → ready → in_transit → delivered/rejected/cancelled`.
- GPS logging only active when status = `in_transit`.
- Geofence alert: push notification when vehicle deviates > 1km from planned route.
- No offline queuing — GPS only logs when network available. Post-delivery log is acceptable per NJ CRC.

### Label/QR Generation

- Server-side generation using `segno` (QR) and `python-barcode` (Code128/DataMatrix).
- Output formats: SVG (web display), PDF (print), ZPL (Zebra/Bluetooth thermal printers).
- Bluetooth thermal printing supported from mobile PWA via Web Bluetooth API (paired printers).
- QR encodes: `tendril://{tenant_id}/{entity_type}/{tag_number}` — scannable by mobile PWA camera for instant entity lookup.
- Barcode encodes: raw tag number (for METRC-compatible scanners).
- PWA includes dedicated "Scan" feature: open camera → detect QR → navigate to entity detail page.

### Unit Conversion

- All weights stored internally in grams (DECIMAL 10,2) — the regulatory standard.
- Display layer converts to user preference (metric: g/kg, imperial: oz/lb) based on `weight_unit_preference` in config.
- All API responses include `weight_g` (canonical) and `weight_display` (formatted with unit label).
- Import/input accepts either unit and converts on write.

### Notification Architecture

- Compliance events emit notifications via `notification_service.py`.
- Channels (configurable per tenant): Push (PWA service worker), In-app (notification center), Email.
- Event types that trigger notifications:
  - `destruction_witness_requested` — urgent push to designated witness
  - `transfer_approval_requested` — push to users with `compliance:transfers:approve`
  - `lab_results_completed` — push + in-app to package owner
  - `metrc_sync_failed` — push + email to tenant admin
  - `transfer_delivered` / `transfer_rejected` — push to transfer creator
  - `geofence_deviation` — push to tenant admin
- Witness confirmation has a configurable deadline (default: 4 hours). Reminder sent at 75% elapsed.

### AI Assistant Tools

New read-only tools registered with the AI assistant (Gemini/Ollama):
- `get_compliance_summary` — overview of pending items (untagged plants, packages needing tests, pending transfers)
- `query_packages` — filter packages by status, strain, date, weight
- `query_transfers` — filter transfers by status, date, destination
- `query_lab_results` — filter by package, status, date range
- `get_plant_lineage` — trace clone chain from any tag
- `get_inventory_report` — current inventory by package type and status

### Immutability Guarantees

- `compliance_events` table: no UPDATE/DELETE granted to application role. Append-only enforced at PostgreSQL permission level.
- `inventory_ledger` table: same — corrections are new entries with negative deltas, not edits.
- `destructions` table: no `updated_at`, no soft delete — record is permanent once `witness_confirmed_at` is set.
- Database trigger prevents any UPDATE on these tables as defense-in-depth.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module location | `api/app/compliance/` | Keeps opt-in, doesn't pollute core grows module |
| Tag provisioning | Dual mode (METRC purchased + auto-generate) | METRC requires pre-purchased tags; manual mode needs auto-generation |
| Tag format | METRC 24-char by default | NJ/most-states compatibility; configurable via `tag_prefix` |
| Package creation | Auto on GrowCycle completion | User preference; reduces manual steps in regulated workflow |
| Package batching | Flexible (1:1 or combine) | User chooses at creation time; `package_sources` join table supports both |
| Transfer approval | Manager required before dispatch | Regulatory accountability; `compliance:transfers:approve` permission |
| Witness flow | Async via push notification | Performers and witnesses don't need to be co-located |
| Multi-location | Facilities table, multiple per tenant | NJ allows multiple licensed locations per entity |
| Event immutability | DB-level triggers + no UPDATE grants | Regulatory evidence cannot be tampered with |
| METRC sync | Async via scheduler worker | Never block user operations on external API |
| GPS storage | JSONB array (v1) | Simple, no PostGIS dependency; upgrade path clear |
| GPS offline | No offline queuing | Post-delivery log acceptable per NJ CRC; simplifies implementation |
| Lab results | Manual + COA upload (v1) | Lab APIs are fragmented; manual covers 100% of cases |
| Encryption | Fernet symmetric for METRC keys | Matches existing secret handling patterns |
| QR library | `segno` | Pure Python, no C deps, small footprint |
| Thermal printing | Web Bluetooth API from PWA | Supports Bluetooth thermal printers from mobile |
| QR scan lookup | PWA camera → entity detail | Fast lookup in facility without manual search |
| Weight storage | DECIMAL(10,2) grams internally | Regulatory standard; display converts to user preference |
| Weight display | Metric + imperial (configurable) | User preference stored in config; API returns both |
| AI integration | Full read access to compliance | AI can answer compliance queries; no write actions |
| Notifications | Push + in-app + email (all channels) | Configurable per tenant; critical for witness/approval flows |
| Reports | On-demand only | User triggers when needed; no automated schedule |
| Web UI | Full compliance dashboard in v1 | Web UI, PWA, API all first-class |

### Alternatives Considered

- **Separate microservice**: Rejected — Tendril is a monorepo; adding a service boundary adds deployment complexity without clear benefit at current scale.
- **Event sourcing for all compliance data**: Rejected for v1 — the compliance_events table provides an event log without requiring full CQRS architecture. Can upgrade later.
- **PostGIS for GPS**: Deferred — JSONB is adequate for v1 route logging. PostGIS adds operational complexity.
- **Synchronous witness flow**: Rejected — requiring both parties on-device simultaneously is impractical in a facility setting.
- **Single location per tenant**: Rejected — NJ operators commonly hold multiple licenses/locations.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| METRC API changes/downtime | Async sync with retry + manual fallback mode |
| Weight discrepancies between Tendril and METRC | Reconciliation report endpoint; ledger provides full audit trail |
| Regulatory requirements vary by state | Provider pattern allows per-state adapters; NJ-first proves the pattern |
| GPS battery drain on mobile | Configurable interval; user can disable for short routes |
| Large JSONB arrays (GPS logs on long routes) | Pagination on read; max 10,000 points per transfer; archive to S3 if exceeded |
| Feature complexity bloats the codebase | Strict module boundary — compliance/ has no imports from grows/ except models |
| Bluetooth thermal printer compatibility | Web Bluetooth API has limited browser support; PDF fallback for incompatible browsers |
| Witness notification missed | Reminder at 75% deadline + escalation to tenant admin if deadline exceeded |

## Migration Plan

1. Add new tables via Alembic migration (non-destructive — new tables + nullable FKs): `facilities`, `plant_tags`, `packages`, `package_sources`, `inventory_ledger`, `lab_tests`, `transfers`, `transfer_packages`, `destructions`, `compliance_events`, `tenant_compliance_config`
2. Add `plant_tag_id` nullable FK to `buckets` table
3. Add DB triggers preventing UPDATE/DELETE on immutable tables
4. Seed `tenant_compliance_config` for existing commercial tenants (disabled by default)
5. Register compliance permissions in RBAC system
6. No data backfill required — existing grows don't retroactively need compliance data

### Rollback
- Drop new tables (no data loss to existing features)
- Remove nullable FK from buckets
- Feature flag (`compliance_enabled`) means the module can be deployed dark

## Resolved Questions

| Question | Answer |
|----------|--------|
| Bluetooth thermal printing in v1? | Yes — via Web Bluetooth API from PWA |
| Web UI in Phase 1? | Yes — full Web UI, PWA, and API are all first-class |
| Offline GPS queuing? | No — not needed, post-delivery log acceptable |
| NJ CRC real-time GPS? | No — post-delivery log is acceptable |
| Tag provisioning model? | Dual — METRC mode uses pre-purchased tags, manual mode auto-generates |
| Witness UX? | Async — push notification to witness, confirm from their device |
| Transfer approval? | Required — manager must approve before dispatch |
| Multi-location? | Yes — facilities table, multiple per tenant |
| AI access? | Full read access — AI tools for compliance queries |
| Notifications? | All channels — push, in-app, email (configurable per tenant) |
| Weight units? | Both metric and imperial — stored as grams, displayed per preference |
| Package from multiple plants? | Flexible — user chooses 1:1 or batch at creation |
| Reporting cadence? | On-demand only |
