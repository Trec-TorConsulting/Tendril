## MODIFIED Requirements

### Requirement: Bucket CRUD
The system SHALL support creating, reading, updating, and deleting buckets with position, label, strain, growth stage, status, notes, and key milestone dates.

Buckets SHALL optionally reference a `plant_tag_id` linking the bucket to its compliance plant tag (for commercial tenants with compliance enabled).

#### Scenario: Create bucket
- **WHEN** a user creates a bucket via `POST /api/buckets` with tent_id, position, and label
- **THEN** the bucket is persisted with a composite ID `{tent_id}-{position}`

#### Scenario: Update bucket metadata
- **WHEN** a user updates a bucket's strain, growth stage, status, notes, or milestone dates
- **THEN** the changes are persisted and reflected in the UI

#### Scenario: Delete bucket cascades
- **WHEN** a user deletes a bucket
- **THEN** all associated sensor readings, journal entries, and dose profiles are also deleted

#### Scenario: Assign compliance tag to bucket
- **WHEN** a commercial tenant with compliance enabled assigns a plant tag to a bucket
- **THEN** the bucket's `plant_tag_id` is set to reference the PlantTag record
- **AND** the bucket detail view displays the tag number and QR code
