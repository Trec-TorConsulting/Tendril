# Capability Delta: Plant Propagation (Mothers & Cloning)

## ADDED Requirements

### Requirement: Space and Grow Purpose Designation
The system SHALL support a `purpose` attribute on both grow spaces (tents) and grows (grow cycles)
with the values `production`, `mother`, and `clone`, defaulting to `production`. The grow's
`purpose` SHALL be authoritative for behavior; a space's `purpose` SHALL act as the default that
pre-selects the purpose when a new grow is created in that space.

#### Scenario: Default purpose is production
- **WHEN** a tent or grow is created without specifying a purpose
- **THEN** its `purpose` is persisted as `production`
- **AND** existing tents and grows created before this feature behave exactly as before

#### Scenario: Create a Mother Keeping space
- **WHEN** a user creates or edits a tent and sets `purpose = mother`
- **THEN** the tent is labeled as a Mother Keeping space in the UI
- **AND** creating a new grow in that tent pre-selects `purpose = mother`

#### Scenario: Purpose drives behavior on the grow
- **WHEN** a grow has `purpose = mother` or `purpose = clone`
- **THEN** the platform applies the corresponding playbook, alert ranges, and AI context for that
  purpose regardless of the tent it lives in

#### Scenario: Filter and badge by purpose
- **WHEN** a user views the grows or tents list
- **THEN** each item displays a purpose badge (Production / Mother / Clone)
- **AND** the user can filter the list by purpose

### Requirement: Mother Keeping Grow Mode
The system SHALL provide a perpetual vegetative "Mother Keeping" mode for grows with
`purpose = mother`, layered on the grow's chosen medium grow type. Mothers SHALL NOT be advanced
to the `flowering` stage, and the grow SHALL be treated as perpetual (no required end date and
excluded from harvest/yield rollups).

#### Scenario: Mother grow stays vegetative
- **WHEN** a user or automation attempts to advance a `purpose = mother` grow to the `flowering`
  stage
- **THEN** the transition is rejected with a clear message that mothers are kept in perpetual veg

#### Scenario: Mother keeping is medium-agnostic
- **WHEN** a mother grow is created with any medium grow type (e.g., `soil`, `coco`, `dwc`)
- **THEN** the grow uses that medium's sensors and mechanics while overlaying the Mother Keeping
  playbook for nutrition, light, and tasks

#### Scenario: Perpetual grows excluded from yield analytics
- **WHEN** harvest/yield analytics are computed
- **THEN** grows with `purpose ∈ {mother, clone}` are excluded from harvest and yield totals

### Requirement: Mother Stock Registry and Vigor
The system SHALL represent each mother plant as a bucket with `role = mother` and SHALL track its
identity (label, strain, origin: seed | clone | purchased, date established, generation), a running
count of clones taken, and a vigor/health indicator suitable for deciding readiness to take
cuttings.

#### Scenario: Register a mother plant
- **WHEN** a user adds a plant to a mother grow
- **THEN** the plant is stored as a bucket with `role = mother`, its strain, origin, and
  established date

#### Scenario: Clone-take history per mother
- **WHEN** cuttings are taken from a mother
- **THEN** the mother's clone-take count and history (dates, quantities, success outcomes) are
  updated and viewable on the mother's detail view

#### Scenario: Vigor gating before cutting
- **WHEN** a mother's recent health indicates stress (e.g., low vigor or an active pest/deficiency
  flag)
- **THEN** the take-clones flow surfaces a caution advising against taking cuttings until the
  mother recovers, per the cannabis-first quality philosophy

### Requirement: Mother Nutrition and Environment Playbook
The system SHALL provide a Mother Keeping playbook that defines a maintenance nutrition schedule
(reduced-strength balanced vegetative feed) and a perpetual vegetative environment target
(vegetative photoperiod such as 18/6, veg VPD/temperature/humidity ranges). Alerting for mother
grows SHALL use vegetative ranges perpetually.

#### Scenario: Maintenance feeding guidance
- **WHEN** a user views feeding advice for a mother grow
- **THEN** the advice reflects a maintenance vegetative formula (lower strength than production
  veg) and includes light root/vitamin support appropriate for stock plants

#### Scenario: Vegetative light schedule enforced
- **WHEN** a mother grow's light schedule is configured
- **THEN** the system recommends and defaults to a vegetative photoperiod and warns against any
  flip to a flowering photoperiod

#### Scenario: Perpetual veg alert ranges
- **WHEN** environmental readings are evaluated for a mother grow
- **THEN** thresholds use vegetative ideal ranges (never flowering ranges), regardless of elapsed
  time

### Requirement: Cloning Grow Type
The system SHALL add a first-class `cloning` grow type with propagation stages
(cutting/sticking → callus → rooting → hardening → ready-to-transplant), clone-specific relevant
sensors (dome/ambient humidity, media or water temperature, misting cycle where applicable, root
development), propagation tasks, health checks, common problems, and propagation-specific
terminology (Cutting, Site, Dome). The grow type SHALL be seeded through the existing grow-type
profile/config pipeline.

#### Scenario: Cloning grow type is available
- **WHEN** a user lists grow types
- **THEN** `cloning` appears with its name, description, and category (propagation)

#### Scenario: Cloning stages and health checks
- **WHEN** a user opens the `cloning` grow type configuration
- **THEN** it returns propagation stages with per-stage environment targets, tasks, health checks,
  and troubleshooting tailored to rooting cuttings (high humidity, low light, no strong nutrients)

#### Scenario: Cloning terminology applied
- **WHEN** the UI renders a cloning grow
- **THEN** container/site terminology uses propagation terms (e.g., "Site", "Cutting", "Dome")

### Requirement: Clone Kit Catalog and Site Generation
The system SHALL expose a read-only catalog of clone kit presets (including Clone King 25/36/64,
EZ-Clone 32/64/128, TurboKlone T24/T48, a deep-water bubble cloner, and a rockwool/rapid-rooter
tray, plus a custom option). Each preset SHALL define its method, site count, sensor kit, and
default media. Selecting a preset when creating a cloning grow SHALL auto-generate that many clone
site buckets.

#### Scenario: List clone kits
- **WHEN** `GET /v1/clone-kits` is called
- **THEN** the catalog of presets is returned with `id`, `name`, `brand`, `method`, `site_count`,
  `sensor_kit`, and `default_media`

#### Scenario: Auto-generate clone sites from a kit
- **WHEN** a user creates a cloning grow and selects the "Clone King 36" preset
- **THEN** the grow is created with 36 buckets of `role = clone_site`, each with `clone_status = empty`

#### Scenario: Custom kit site count
- **WHEN** a user selects the custom kit option and enters a site count and method
- **THEN** the grow is created with that many clone sites using the chosen method

### Requirement: Clone Site and Batch Tracking
The system SHALL track each rooting cutting via a clone site (`role = clone_site` bucket) and an
append-only `clone_records` ledger. Each clone record SHALL capture the source mother, strain,
cloning grow, method, cut date, rooting status (`rooting` | `rooted` | `failed` | `transplanted`),
root development, and outcome, so history is preserved even when sites are reused.

#### Scenario: Clone site status lifecycle
- **WHEN** a cutting is placed in a clone site
- **THEN** the site's `clone_status` becomes `occupied`/`rooting` and a `clone_records` row is
  created with `status = rooting` and the cut date

#### Scenario: Mark a clone rooted
- **WHEN** a user marks a clone as rooted
- **THEN** the clone record's `status = rooted` and `rooted_at` are set and the site reflects
  `rooted`

#### Scenario: Mark a clone failed
- **WHEN** a cutting dies
- **THEN** the clone record's `status = failed` is recorded and the site is freed
  (`clone_status = empty`) for reuse while the failed record remains in the ledger for analytics

#### Scenario: Reused site preserves history
- **WHEN** a freed clone site is used for a new cutting
- **THEN** a new `clone_records` row is created and prior records for that site remain intact

### Requirement: Take Clones From a Mother
The system SHALL provide an action to take one or more cuttings from a mother into a cloning grow,
creating one clone record per cutting, occupying available clone sites, linking lineage
(mother → clone), and journaling the event on the mother.

#### Scenario: Take multiple cuttings
- **WHEN** a user invokes take-clones on a mother with a count and a destination cloning grow
- **THEN** that many clone records are created (each linked to the mother and its strain), assigned
  to available clone sites set to `rooting`, and a journal entry is recorded on the mother

#### Scenario: Insufficient open sites
- **WHEN** the requested cutting count exceeds available empty clone sites in the destination grow
- **THEN** the action is rejected (or clamped with an explicit warning) and no partial, orphaned
  records are created

#### Scenario: Lineage recorded at cut time
- **WHEN** a cutting is taken
- **THEN** its clone record references the originating `mother_bucket_id` and `strain_id`

### Requirement: Promote a Rooted Clone Into a Grow
The system SHALL support promoting a rooted clone site into a destination grow in any tent/medium
via a single atomic action. Promotion SHALL create a new plant site in the destination grow with
`planting_method = clone`, record lineage (mother → clone → plant), free the originating clone
site, and journal both sides.

#### Scenario: Promote a rooted clone
- **WHEN** a user promotes a rooted clone record into a destination grow
- **THEN** a new bucket is created in that grow with `planting_method = clone`, `mother_bucket_id`
  and `source_clone_record_id` set from the record, and the strain inherited (overridable)

#### Scenario: Clone record and site updated on promotion
- **WHEN** promotion succeeds
- **THEN** the clone record is set to `status = transplanted` with `transplanted_at` and
  `dest_bucket_id`, and the originating clone site is freed (`clone_status = empty`) for reuse

#### Scenario: Guard against promoting unrooted clones
- **WHEN** a user attempts to promote a clone that is `rooting`, `failed`, or already
  `transplanted`
- **THEN** the action is rejected unless explicitly forced, with a clear reason

#### Scenario: Destination must be a valid same-tenant grow
- **WHEN** the destination grow does not belong to the tenant or is the cloning grow itself
- **THEN** the promotion is rejected

#### Scenario: Atomic promotion
- **WHEN** any step of promotion fails
- **THEN** the entire operation rolls back, leaving the clone record and both grows unchanged

### Requirement: Plant Lineage Graph
The system SHALL maintain lightweight plant lineage for all growers, linking each plant/site to its
parent mother and originating clone record, and SHALL expose lineage lookup (ancestors and
descendants). When compliance plant tags are present (see `bucket-monitoring`), lineage SHALL
surface the associated tag but SHALL NOT require it.

#### Scenario: View a plant's ancestry
- **WHEN** a user opens lineage for a promoted plant
- **THEN** the system returns its source clone record and mother (and, if available, the mother's
  own origin)

#### Scenario: View a mother's descendants
- **WHEN** a user opens lineage for a mother
- **THEN** the system returns the clones taken from it and the plants those clones became

#### Scenario: Lineage works without compliance
- **WHEN** a tenant has no compliance/plant-tag data
- **THEN** lineage still resolves using built-in mother/clone references

#### Scenario: Lineage surfaces compliance tag when present
- **WHEN** a bucket in the lineage has a linked plant tag
- **THEN** the tag identifier is included in the lineage response

### Requirement: Propagation Analytics
The system SHALL compute and expose propagation analytics, including clone success rate and average
days-to-root, aggregated per mother and per strain, derived from the `clone_records` ledger.

#### Scenario: Per-mother success rate
- **WHEN** a user views a mother's analytics
- **THEN** the system reports clone success rate (rooted+transplanted / total) and average
  days-to-root for that mother

#### Scenario: Per-strain propagation trends
- **WHEN** a user views propagation analytics for a strain
- **THEN** the system aggregates success rate and days-to-root across all mothers of that strain

### Requirement: AI Coaching and Alerting for Mothers and Clones
The system SHALL inject mother/clone purpose into AI context and SHALL produce recommendations,
alerts, and coach tips that follow the cannabis-first quality philosophy for propagation: preserve
genetics, keep mothers low-stress and disease-free, never recommend flowering a mother, and guide
cuttings toward high-humidity/low-light rooting. Clone troubleshooting SHALL be available.

#### Scenario: Mother coaching preserves genetics
- **WHEN** the AI evaluates a mother grow
- **THEN** its advice prioritizes vigor, sanitation, and stability (never a flower flip or
  yield-chasing feed)

#### Scenario: Clone environment coaching
- **WHEN** the AI evaluates a cloning grow
- **THEN** it recommends high humidity, minimal light, and no strong nutrients during rooting, and
  flags conditions that cause damping-off or failure to root

#### Scenario: Clone troubleshooting
- **WHEN** a user reports clones wilting or not rooting
- **THEN** the assistant provides propagation-specific troubleshooting (humidity, dome, media
  moisture, rooting hormone, sanitation, temperature)

### Requirement: Access Control and Plan Availability
Mother keeping and cloning features SHALL be available on all billing plans and SHALL enforce the
platform's existing RBAC and grow-scoped access controls. Mutating actions (create/take/promote)
SHALL require an editor role; read actions SHALL be available to viewers with access to the grow.

#### Scenario: Available on all plans
- **WHEN** a tenant on any plan uses mother/clone features
- **THEN** the features are accessible without a plan gate

#### Scenario: Editor role required for mutations
- **WHEN** a viewer-role user attempts to take clones or promote a clone
- **THEN** the request is rejected with an authorization error

#### Scenario: Grow-scoped access respected
- **WHEN** a user is restricted to specific grows
- **THEN** they can only view/act on mothers, clone sites, and lineage within their permitted grows

### Requirement: Data Integrity, Migration, and Backward Compatibility
The schema changes SHALL be additive and reversible: new columns SHALL be nullable or defaulted,
the `Bucket.role` value set SHALL be extended (not repurposed), the new `clone_records` table SHALL
enforce tenant isolation via Row-Level Security, and a rollback SHALL restore the prior schema
without data loss for existing grows.

#### Scenario: Additive migration preserves existing data
- **WHEN** the migration is applied to a database with existing tents, grows, and buckets
- **THEN** all existing rows gain `purpose = production` (tents/grows) and null propagation fields
  (buckets), with no behavior change

#### Scenario: Tenant isolation on clone records
- **WHEN** a query reads `clone_records`
- **THEN** RLS restricts rows to the current tenant, consistent with other tenant-scoped tables

#### Scenario: Reversible rollback
- **WHEN** the migration is rolled back
- **THEN** the `clone_records` table and the added columns are removed and pre-existing grows
  continue to function

### Requirement: Full CRUD and API Conventions
The system SHALL expose Create, Read (single + list), Update, and Delete for new mutable resources
(clone records, mother/clone-site buckets via existing bucket endpoints) and read endpoints for
derived data (clone-kit catalog, lineage, propagation analytics), following the platform's API
design and validation conventions with Pydantic input models.

#### Scenario: Clone record CRUD
- **WHEN** a client creates, reads, lists, updates, or deletes a clone record via the API
- **THEN** each operation is implemented, tenant-scoped, and input-validated

#### Scenario: Read-only derived endpoints
- **WHEN** a client requests the clone-kit catalog, lineage, or propagation analytics
- **THEN** read endpoints return the derived data without exposing mutation of computed views
