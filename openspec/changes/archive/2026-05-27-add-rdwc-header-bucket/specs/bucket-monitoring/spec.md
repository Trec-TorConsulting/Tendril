## ADDED Requirements

### Requirement: Bucket Role (Header vs Site)
The system SHALL support a `role` field on buckets with values `site` (default) and `header` to distinguish RDWC control/header buckets from individual site buckets.

#### Scenario: Create header bucket
- **WHEN** a user creates a bucket with `role: "header"` in an RDWC grow
- **THEN** the bucket is persisted with role=header and displayed with a "Header" badge in the UI

#### Scenario: Update bucket role
- **WHEN** a user changes a bucket's role from site to header via PATCH
- **THEN** subsequent sensor readings for that bucket propagate to all sibling site buckets

#### Scenario: Default role for existing buckets
- **WHEN** the migration runs on existing data
- **THEN** all existing buckets receive role=site (no behavior change)


### Requirement: Header Bucket Reading Propagation
The system SHALL automatically duplicate sensor readings from a header bucket to all site buckets in the same grow cycle.

#### Scenario: Propagate on sensor write
- **WHEN** a sensor reading is persisted to a bucket with role=header
- **THEN** identical readings (pH, EC, PPM, water_temp, DO, flow_rate, water_level) are created for every sibling bucket with role=site in the same grow_cycle_id

#### Scenario: No propagation for site buckets
- **WHEN** a sensor reading is persisted to a bucket with role=site
- **THEN** no propagation occurs — only the target bucket receives the reading

#### Scenario: Propagation across all connectors
- **WHEN** any connector (Tuya, Pulse, Ecowitt) writes a bucket reading
- **THEN** the propagation logic is invoked identically regardless of connector type


## MODIFIED Requirements

### Requirement: Bucket Detail View
_(Add to existing)_

#### Scenario: Header badge display
- **WHEN** a bucket has role=header
- **THEN** the bucket card displays a blue "Header" badge alongside existing stage/status badges
