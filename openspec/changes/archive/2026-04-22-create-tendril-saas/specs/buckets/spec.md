## ADDED Requirements

### Requirement: Tenant-Scoped Bucket CRUD
The system SHALL provide full CRUD operations for buckets, scoped to the authenticated tenant with grow linkage.

#### Scenario: Create bucket linked to grow
- **WHEN** a user creates a bucket with tent_id and grow_cycle_id
- **THEN** the bucket is created with the user's tenant_id, linked to the specified grow, and inherits the grow type's default fields and sensor configuration

#### Scenario: Grow-type-aware bucket form
- **WHEN** a user creates or edits a bucket
- **THEN** the form shows only fields relevant to the grow type (e.g., DWC: reservoir size, air stone status; Coco: pot size, perlite ratio, CalMag; Soil: pot size, soil type, organic/synthetic; NFT: channel position)

#### Scenario: Bucket detail with sub-resources
- **WHEN** a user requests a bucket by ID
- **THEN** the system returns bucket data with latest sensor readings, stage, strain info, and grow linkage

### Requirement: Bucket Journal
The system SHALL provide CRUD operations for bucket journal entries, scoped to the authenticated tenant.

#### Scenario: Add journal entry
- **WHEN** a user adds a journal entry to a bucket
- **THEN** the entry is stored with timestamp, content, and tenant_id

### Requirement: Bucket Photos
The system SHALL provide upload, list, caption update, and delete operations for bucket photos, scoped to the authenticated tenant.

#### Scenario: Upload photo
- **WHEN** a user uploads a photo for a bucket
- **THEN** the photo is stored and associated with the bucket and tenant

### Requirement: Bucket Stage Management
The system SHALL support growth stage tracking with advance, milestones, and AI-powered stage suggestions.

#### Scenario: Advance stage
- **WHEN** a user advances a bucket's growth stage
- **THEN** the stage is updated, a milestone is recorded, and the stage history is preserved

### Requirement: Bucket Yields
The system SHALL provide CRUD operations for yield records per bucket, scoped to the authenticated tenant.

#### Scenario: Record yield
- **WHEN** a user records a yield for a bucket
- **THEN** the yield is stored with weight, quality rating, and harvest date
