## ADDED Requirements

### Requirement: Facility Management
The system SHALL support multiple licensed facilities per tenant. Each facility SHALL have a name, license number, license type, full address, and optional GPS coordinates.

At least one facility MUST be configured when compliance is enabled. Tags, packages, and transfers SHALL be associated with a specific facility.

#### Scenario: Create a facility
- **WHEN** a tenant admin creates a facility with license number, address, and license type
- **THEN** the system persists the facility record
- **AND** it is available for association with tags, packages, and transfers

#### Scenario: Inter-facility transfer
- **WHEN** a transfer is created with transfer_type `internal` between two facilities of the same tenant
- **THEN** the system allows the transfer without external license verification
- **AND** packages move from origin facility to destination facility on delivery

---

### Requirement: Plant Tag Management
The system SHALL provide individual plant tag management with dual provisioning modes: (1) METRC purchased tags where users enter pre-purchased tag numbers, and (2) auto-generated tags for manual/non-METRC compliance modes.

Each plant tag SHALL be a 24-character string conforming to METRC tag format. Tags SHALL be unique per tenant. A Bucket SHALL have at most one active plant tag. Tags SHALL NOT be reassigned — if a tag is assigned in error, it MUST be voided and a new tag created.

Tags SHALL track clone lineage via a `source_tag_id` reference, enabling mother-to-clone chain-of-custody traceability. Tags SHALL progress through states: `available → active → harvested/destroyed/transferred/voided`.

#### Scenario: Provision METRC purchased tags (bulk import)
- **WHEN** a user imports a batch of pre-purchased METRC tag numbers
- **THEN** the system creates PlantTag records with status `available` and `provisioning_mode = metrc_purchased`
- **AND** tags are ready for assignment to Buckets

#### Scenario: Auto-generate tags (manual mode)
- **WHEN** a user assigns a tag in manual compliance mode and no pre-provisioned tag is specified
- **THEN** the system generates a unique 24-char tag number using the tenant's `tag_prefix`
- **AND** creates the PlantTag with `provisioning_mode = auto_generated`

#### Scenario: Assign plant tag to bucket
- **WHEN** a commercial tenant user assigns a plant tag to a Bucket
- **THEN** the system links the PlantTag to the Bucket and sets status to `active`
- **AND** emits a `plant_tagged` compliance event with full state snapshot
- **AND** generates a QR code and barcode for the tag

#### Scenario: Attempt to reassign existing tag
- **WHEN** a user attempts to assign an already-active tag to a different Bucket
- **THEN** the system rejects the operation with a 409 Conflict error
- **AND** no state changes occur

#### Scenario: Clone lineage tracking
- **WHEN** a user assigns a tag to a clone Bucket and specifies the mother plant's tag
- **THEN** the system records the `source_tag_id` reference
- **AND** the lineage chain is queryable from any descendant tag

#### Scenario: Void a tag
- **WHEN** a user voids an erroneously assigned tag
- **THEN** the tag status transitions to `voided`
- **AND** the Bucket's `plant_tag_id` is cleared
- **AND** a new tag can be assigned to that Bucket

---

### Requirement: Package Management
The system SHALL automatically create Packages from completed harvests when a GrowCycle transitions to `completed` status (curing finished). Package creation SHALL be flexible — users can configure 1:1 (one package per yield) or batch (multiple yields combined into one package).

Packages track their source yields via a `package_sources` join table, supporting both single-plant and multi-plant packages. Each Package SHALL receive a unique package tag in METRC 24-char format.

Packages SHALL transition through states: `created → testing → available → on_hold → transferred/destroyed/empty`. A Package SHALL NOT be transferred unless its `qc_status` is `passed` or `exempt`.

#### Scenario: Auto-create packages on grow completion (1:1 mode)
- **WHEN** a GrowCycle transitions to status `completed` and tenant uses 1:1 packaging
- **THEN** the system creates one Package per Yield record in that GrowCycle
- **AND** creates a `package_sources` entry linking the package to its yield and plant tag
- **AND** sets `initial_weight_g` and `current_weight_g` from the Yield dry weight
- **AND** creates an inventory ledger entry of type `created`
- **AND** emits a `package_created` compliance event

#### Scenario: Auto-create batch package (combine mode)
- **WHEN** a GrowCycle transitions to status `completed` and tenant uses batch packaging
- **THEN** the system creates one Package combining all Yields of the same strain
- **AND** creates multiple `package_sources` entries (one per contributing yield)
- **AND** `initial_weight_g` equals the sum of all contributing yield dry weights

#### Scenario: Attempt to transfer package without passing lab test
- **WHEN** a user attempts to add a Package with `qc_status = pending` or `failed` to a Transfer
- **THEN** the system rejects the operation with a 422 error
- **AND** returns a message indicating lab testing must pass first

#### Scenario: Split a package
- **WHEN** a user splits a Package into two new Packages
- **THEN** the original Package weight is decremented by the split amount
- **AND** a new Package is created with the split weight
- **AND** inventory ledger entries are created for both (negative on source, positive on new)
- **AND** the sum of all resulting package weights equals the original weight

---

### Requirement: Inventory Ledger
The system SHALL maintain an append-only inventory ledger recording every weight change for every Package. The ledger SHALL be immutable — no UPDATE or DELETE operations permitted at the database level.

Every weight mutation (creation, sampling, transfer, destruction, adjustment, split, merge) SHALL create a ledger entry with the weight delta and resulting balance. The `current_weight_g` on the Package SHALL always equal the latest `balance_after_g` in the ledger.

#### Scenario: Weight consistency enforcement
- **WHEN** any operation modifies a Package's weight
- **THEN** the system creates an inventory_ledger entry with the delta and new balance
- **AND** updates the Package `current_weight_g` to match
- **AND** the sum of all ledger deltas for a Package equals `current_weight_g`

#### Scenario: Attempt to update ledger entry
- **WHEN** any database operation attempts to UPDATE or DELETE an inventory_ledger row
- **THEN** the database trigger rejects the operation
- **AND** returns an error indicating the ledger is immutable

#### Scenario: Weight reconciliation report
- **WHEN** a user requests a reconciliation report
- **THEN** the system compares Package `current_weight_g` against the latest ledger `balance_after_g`
- **AND** flags any discrepancies for investigation

---

### Requirement: Lab Testing Workflow
The system SHALL support recording lab test results for Packages, including potency, terpenes, contaminants, and Certificate of Analysis (COA) document upload.

Lab tests SHALL transition through states: `submitted → in_progress → completed/failed`. On completion, the Package `qc_status` SHALL be updated to `passed` or `failed` based on the test result.

#### Scenario: Record lab test results
- **WHEN** a user submits lab test results for a Package
- **THEN** the system creates a LabTest record linked to the Package
- **AND** creates an inventory ledger entry for the sample weight deduction
- **AND** emits a `lab_submitted` compliance event

#### Scenario: Lab test passes
- **WHEN** a lab test status transitions to `completed` with result `pass`
- **THEN** the Package `qc_status` is updated to `passed`
- **AND** the Package `lab_test_id` is updated to reference this test
- **AND** a `lab_completed` compliance event is emitted

#### Scenario: Upload Certificate of Analysis
- **WHEN** a user uploads a COA PDF for a lab test
- **THEN** the system stores the file via S3-compatible storage
- **AND** records the storage key in `coa_storage_key`
- **AND** the COA is retrievable via a signed URL

---

### Requirement: Transfer Manifests with GPS Tracking
The system SHALL support creating transfer manifests for moving Packages between licensed facilities. Transfers SHALL require manager approval before dispatch. Transfers SHALL include driver, vehicle, route, and GPS tracking data.

Transfer status flow: `draft → pending_approval → approved → ready → in_transit → delivered/rejected/cancelled`. Manager approval requires `compliance:transfers:approve` permission.

GPS coordinates SHALL be logged at configurable intervals during transit. The system SHALL send a push notification if the vehicle deviates more than 1km from the planned route.

#### Scenario: Submit transfer for approval
- **WHEN** a user completes a Transfer manifest (packages, destination, driver info)
- **AND** submits it for approval
- **THEN** the Transfer status transitions to `pending_approval`
- **AND** a push notification is sent to users with `compliance:transfers:approve` permission

#### Scenario: Manager approves transfer
- **WHEN** a user with `compliance:transfers:approve` permission approves a pending transfer
- **THEN** the Transfer status transitions to `approved`
- **AND** `approved_by` and `approved_at` are recorded
- **AND** the transfer creator is notified

#### Scenario: Manager rejects transfer
- **WHEN** a user with `compliance:transfers:approve` permission rejects a pending transfer with a note
- **THEN** the Transfer status transitions back to `draft`
- **AND** `rejection_note` is recorded
- **AND** the transfer creator is notified with the rejection reason

#### Scenario: Dispatch an approved transfer
- **WHEN** a user transitions an approved Transfer to `in_transit`
- **THEN** the system emits a `transfer_departed` compliance event
- **AND** creates `transfer_out` inventory ledger entries for all included Packages
- **AND** GPS tracking becomes active for the transfer

#### Scenario: Log GPS coordinates during transit
- **WHEN** the mobile client sends GPS coordinates for an in-transit Transfer
- **THEN** the system appends the point (lat, lng, timestamp) to `gps_log`
- **AND** checks for route deviation against `planned_route`
- **AND** if deviation > 1km, sends a push notification to the tenant admin

#### Scenario: Deliver a transfer
- **WHEN** the receiving facility confirms delivery with received weights
- **THEN** the Transfer status transitions to `delivered`
- **AND** `weight_received_g` is recorded per package
- **AND** a `transfer_delivered` compliance event is emitted
- **AND** any weight discrepancy (shipped vs received) is flagged
- **AND** the transfer creator receives a delivery notification

#### Scenario: Reject a transfer
- **WHEN** the receiving facility rejects a transfer
- **THEN** the Transfer status transitions to `rejected`
- **AND** a rejection reason is recorded
- **AND** the source Packages are restored to `available` status
- **AND** inventory ledger reversal entries (`transfer_in`) are created

---

### Requirement: Witnessed Destruction
The system SHALL support recording the destruction of plants or packages with a mandatory witness and photographic evidence. The witness flow SHALL be asynchronous — the performer logs the destruction, and the designated witness receives a push notification to confirm from their own device.

Destruction SHALL require: (1) a performing user, (2) a different witnessing user who confirms asynchronously, (3) at least one photo, and (4) a stated reason and method. Witness confirmation SHALL have a configurable deadline (default: 4 hours) with a reminder at 75% elapsed time.

#### Scenario: Initiate destruction with witness notification
- **WHEN** a user records destruction of a Package and designates a witness
- **AND** at least one photo is uploaded
- **THEN** the system creates a pending destruction record
- **AND** sends a push notification to the designated witness requesting confirmation

#### Scenario: Witness confirms destruction
- **WHEN** the designated witness confirms the destruction from their device
- **THEN** `witness_confirmed_at` is set to the current timestamp
- **AND** the Package/PlantTag status transitions to `destroyed`
- **AND** a `destruction` inventory ledger entry is created
- **AND** a `destruction_completed` compliance event is emitted

#### Scenario: Witness deadline expires
- **WHEN** the witness confirmation deadline elapses without confirmation
- **THEN** the system sends a reminder notification at 75% elapsed
- **AND** if the deadline fully expires, escalates to the tenant admin

#### Scenario: Attempt destruction without witness
- **WHEN** a user attempts to initiate a destruction where `witnessed_by` equals `performed_by`
- **THEN** the system rejects the operation with a 422 error
- **AND** no state changes occur

#### Scenario: Attempt destruction without photo
- **WHEN** a user attempts to initiate a destruction with an empty `photo_storage_keys` array
- **THEN** the system rejects the operation with a 422 error indicating photo evidence is required

---

### Requirement: Immutable Compliance Event Log
The system SHALL maintain an append-only compliance event log recording every significant action in the seed-to-sale lifecycle. Events SHALL be immutable at the database level.

Each event SHALL capture: event type, entity reference, acting user, and a full JSONB snapshot of the entity state at event time. Events SHALL track METRC synchronization status.

#### Scenario: Compliance event creation
- **WHEN** any compliance-significant action occurs (tag assignment, package creation, transfer, destruction, lab test)
- **THEN** the system appends a compliance_event record
- **AND** the event includes a full state snapshot in `payload`
- **AND** `metrc_synced` defaults to false

#### Scenario: Attempt to modify compliance event
- **WHEN** any database operation attempts to UPDATE or DELETE a compliance_event row
- **THEN** the database trigger rejects the operation

#### Scenario: METRC sync
- **WHEN** the scheduler worker processes pending compliance events (where `metrc_synced = false`)
- **AND** the tenant has METRC integration enabled with valid credentials
- **THEN** the system pushes the event to the METRC API
- **AND** on success, sets `metrc_synced = true` and `metrc_synced_at`
- **AND** on failure, records the error in `metrc_error` and notifies the user

---

### Requirement: Tenant Compliance Configuration
The system SHALL allow commercial tenants to configure compliance tracking per-tenant, including enabling/disabling the module, selecting a compliance provider (METRC/manual), and storing encrypted API credentials.

#### Scenario: Enable compliance for a tenant
- **WHEN** a tenant admin enables compliance and provides their license number and state code
- **THEN** the system creates/updates a `tenant_compliance_config` record
- **AND** compliance routes become accessible for that tenant

#### Scenario: Configure METRC integration
- **WHEN** a tenant admin provides METRC API and vendor keys
- **THEN** the system encrypts the keys with Fernet symmetric encryption
- **AND** stores them in `metrc_api_key_encrypted` and `metrc_vendor_key_encrypted`
- **AND** the keys are never returned in API responses (write-only)

#### Scenario: Access compliance without enabling
- **WHEN** a commercial tenant user accesses compliance endpoints without `compliance_enabled = true`
- **THEN** the system returns 403 with a message to enable compliance in settings

---

### Requirement: Label and QR Code Generation
The system SHALL generate QR codes and barcodes for plant tags and package tags, in SVG and PDF formats suitable for printing.

QR codes SHALL encode `tendril://{tenant_id}/{entity_type}/{tag_number}`. Barcodes SHALL use Code128 format encoding the raw tag number.

#### Scenario: Generate label for a plant tag
- **WHEN** a user requests a label for a plant tag
- **THEN** the system generates a QR code and Code128 barcode
- **AND** returns the label in the requested format (SVG, PDF, or ZPL)
- **AND** the QR code is scannable by the mobile PWA for quick entity lookup

#### Scenario: Batch label generation
- **WHEN** a user requests labels for multiple tags/packages
- **THEN** the system generates a multi-page PDF with one label per item
- **AND** labels are arranged for standard label sheet printing (Avery 5160 or similar)

#### Scenario: Bluetooth thermal printing from PWA
- **WHEN** a user pairs a Bluetooth thermal printer via Web Bluetooth API
- **AND** requests a label print
- **THEN** the system sends ZPL-formatted label data to the paired printer
- **AND** the label prints on the thermal printer

---

### Requirement: QR Code Scan Lookup
The system SHALL provide a QR code scanner in the mobile PWA that detects Tendril compliance QR codes and navigates directly to the associated entity detail page.

#### Scenario: Scan plant tag QR
- **WHEN** a user opens the QR scanner in the PWA and scans a Tendril plant tag QR code
- **THEN** the system decodes the `tendril://{tenant_id}/plant_tag/{tag_number}` URI
- **AND** navigates to the plant tag detail page showing the linked Bucket, lineage, and status

#### Scenario: Scan package tag QR
- **WHEN** a user scans a Tendril package QR code
- **THEN** the system navigates to the package detail page showing inventory, lab results, and history

#### Scenario: Scan QR from different tenant
- **WHEN** a user scans a QR code belonging to a different tenant
- **THEN** the system displays an error indicating the entity does not belong to their organization

---

### Requirement: METRC API Integration
The system SHALL integrate with the METRC track-and-trace API, with New Jersey as the primary target state. Integration SHALL be asynchronous — user operations SHALL NOT block on METRC API responses.

The system SHALL support manual review mode (default for v1) where pending events are displayed in a dashboard and the user triggers sync, as well as auto-sync mode where the scheduler worker pushes events automatically.

#### Scenario: Manual METRC sync
- **WHEN** a user reviews pending compliance events in the dashboard
- **AND** triggers a manual sync batch
- **THEN** the system pushes all selected events to the METRC API
- **AND** updates sync status on each event
- **AND** reports successes and failures

#### Scenario: METRC API failure
- **WHEN** the METRC API returns an error during sync
- **THEN** the system records the error in `metrc_error` on the compliance event
- **AND** sends a push notification and email to the tenant admin
- **AND** the event remains in `metrc_synced = false` for retry

#### Scenario: METRC idempotent retry
- **WHEN** a previously-failed sync is retried
- **THEN** the system uses the compliance_event UUID as the idempotency key
- **AND** METRC does not create duplicate records

---

### Requirement: Compliance Notifications
The system SHALL deliver compliance notifications through multiple channels: push notifications (PWA service worker), in-app notification center, and email. Channel selection SHALL be configurable per tenant.

#### Scenario: Witness notification delivery
- **WHEN** a destruction is initiated and a witness is designated
- **THEN** the system sends a push notification to the witness
- **AND** creates an in-app notification entry
- **AND** sends an email if email notifications are enabled

#### Scenario: Transfer approval notification
- **WHEN** a transfer is submitted for approval
- **THEN** the system sends push notifications to all users with `compliance:transfers:approve` permission

#### Scenario: METRC sync failure notification
- **WHEN** a METRC sync attempt fails
- **THEN** the system sends a push notification and email to the tenant admin
- **AND** creates an in-app notification with error details

#### Scenario: Witness reminder
- **WHEN** 75% of the witness confirmation deadline has elapsed without confirmation
- **THEN** the system sends a reminder push notification to the witness

---

### Requirement: AI Assistant Compliance Access
The system SHALL provide read-only compliance query tools to the AI grow assistant, enabling users to ask natural language questions about their compliance state.

#### Scenario: Query compliance summary
- **WHEN** a user asks the AI assistant "what needs attention in compliance?"
- **THEN** the AI uses the `get_compliance_summary` tool
- **AND** returns a summary of untagged plants, packages pending testing, pending transfers, and overdue witness confirmations

#### Scenario: Query package inventory
- **WHEN** a user asks "what packages are ready for transfer?"
- **THEN** the AI uses the `query_packages` tool with status filter `available`
- **AND** returns a list of packages with strain, weight, and package date

#### Scenario: Query plant lineage
- **WHEN** a user asks "show me the lineage for tag X"
- **THEN** the AI uses the `get_plant_lineage` tool
- **AND** returns the mother-to-clone chain with all intermediate tags

---

### Requirement: Weight Unit Display
The system SHALL store all weights internally in grams (DECIMAL 10,2) and display them according to the tenant's `weight_unit_preference` setting (metric or imperial).

All API responses that include weights SHALL provide both `weight_g` (canonical grams value) and `weight_display` (human-formatted string with unit label, e.g., "453.59 g" or "1.00 lb").

#### Scenario: Display weight in imperial
- **WHEN** a tenant has `weight_unit_preference = imperial`
- **AND** a package has `current_weight_g = 453.59`
- **THEN** the API response includes `weight_g: 453.59` and `weight_display: "1.00 lb"`

#### Scenario: Input weight in imperial
- **WHEN** a user enters a weight as "2 oz" in an input field
- **THEN** the system converts to grams (56.70g) for storage
- **AND** displays back in the user's preferred unit

---

### Requirement: On-Demand Compliance Reports
The system SHALL generate compliance reports on-demand when requested by a user. Reports SHALL NOT be auto-generated on a schedule.

Available report types: inventory summary, transfer history, destruction log, plant tag assignment history, lab testing summary, METRC sync status.

#### Scenario: Generate inventory report
- **WHEN** a user requests an inventory report with optional date range and package type filters
- **THEN** the system generates a report summarizing all packages, weights, statuses, and lab test results
- **AND** returns the report as downloadable PDF and/or structured JSON

#### Scenario: Generate transfer history report
- **WHEN** a user requests a transfer history report
- **THEN** the system generates a report with all transfers, manifests, weights, and delivery confirmations
- **AND** includes GPS route summary for each completed transfer
