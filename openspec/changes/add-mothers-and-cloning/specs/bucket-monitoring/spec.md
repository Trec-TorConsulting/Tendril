# Capability Delta: Bucket Monitoring (Mother & Clone-Site Roles)

## ADDED Requirements

### Requirement: Bucket Roles for Mothers and Clone Sites
The system SHALL extend the bucket `role` value set to include `mother` and `clone_site` in
addition to the existing `site` and `header`. A `mother` bucket represents a perpetual stock plant
in a `purpose = mother` grow; a `clone_site` bucket represents a single rooting position in a
`purpose = clone` (`grow_type = cloning`) grow and SHALL expose a `clone_status`
(`empty` | `occupied` | `rooting` | `rooted` | `failed` | `transplanted`). Buckets SHALL also carry
optional lineage references `mother_bucket_id` and `source_clone_record_id`.

#### Scenario: Create a mother bucket
- **WHEN** a bucket is created in a mother grow
- **THEN** it is persisted with `role = mother` and is rendered with a Mother badge in the UI

#### Scenario: Clone site exposes status
- **WHEN** a clone site bucket is read
- **THEN** its `clone_status` reflects the current rooting state of the cutting it holds (or
  `empty`)

#### Scenario: Lineage fields are optional and backward-compatible
- **WHEN** a bucket has no mother or clone origin
- **THEN** `mother_bucket_id` and `source_clone_record_id` are null and the bucket behaves as
  before

#### Scenario: Existing roles unchanged
- **WHEN** buckets with `role = site` or `role = header` are read or written
- **THEN** their behavior is identical to before this change

### Requirement: Clone Promotion Between Grows
The system SHALL support moving a rooted clone site into a destination grow by creating a new
bucket in the destination grow with `planting_method = clone` and lineage references set, then
freeing the originating clone site. This is the only supported mechanism for a bucket to change
grows.

#### Scenario: Promotion creates destination bucket
- **WHEN** a rooted clone is promoted into a destination grow
- **THEN** a new bucket is created in that grow with `planting_method = clone`,
  `mother_bucket_id`, and `source_clone_record_id` populated

#### Scenario: Originating clone site is freed
- **WHEN** promotion completes
- **THEN** the originating `clone_site` bucket's `clone_status` returns to `empty` and it is
  available for a new cutting

#### Scenario: Delete cascade includes clone linkage
- **WHEN** a bucket referenced as a lineage parent is deleted
- **THEN** dependent lineage references are set null (not cascade-deleted), preserving the
  historical clone-record ledger
