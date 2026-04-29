## ADDED Requirements

### Requirement: Multiple Cameras Per Grow Space
The system SHALL support multiple cameras per tent/grow space via a `tent_cameras` table. Each camera SHALL have a label, type, URL, sort order, and primary flag.

#### Scenario: User adds multiple cameras to a tent
- **WHEN** a user navigates to tent settings and adds a camera
- **THEN** the system SHALL create a `tent_cameras` record with the provided label, type, and URL
- **AND** the user SHALL be able to add additional cameras to the same tent

#### Scenario: Camera types supported
- **WHEN** a user configures a camera
- **THEN** the system SHALL accept types: `http_snapshot`, `rtsp`, or `frigate`
- **AND** validate that the URL is appropriate for the selected type

### Requirement: Camera CRUD API
The system SHALL provide RESTful endpoints for managing cameras on a tent.

#### Scenario: List cameras for a tent
- **WHEN** `GET /v1/tents/{tent_id}/cameras` is called
- **THEN** the system SHALL return all cameras for that tent ordered by `sort_order`

#### Scenario: Create a camera
- **WHEN** `POST /v1/tents/{tent_id}/cameras` is called with label, type, and URL
- **THEN** the system SHALL create the camera record
- **AND** if it is the first camera for the tent, set `is_primary = TRUE`

#### Scenario: Update a camera
- **WHEN** `PATCH /v1/tents/{tent_id}/cameras/{camera_id}` is called
- **THEN** the system SHALL update the specified fields (label, url, sort_order, is_primary)

#### Scenario: Delete a camera
- **WHEN** `DELETE /v1/tents/{tent_id}/cameras/{camera_id}` is called
- **THEN** the system SHALL remove the camera record
- **AND** if the deleted camera was primary, promote the next camera by sort_order to primary

### Requirement: Camera Snapshot Endpoint Enhancement
The existing `GET /tents/{tent_id}/camera-snapshot` endpoint SHALL accept an optional `camera_id` query parameter to select which camera to snapshot.

#### Scenario: Snapshot default camera
- **WHEN** `GET /tents/{tent_id}/camera-snapshot` is called without `camera_id`
- **THEN** the system SHALL return a snapshot from the primary camera (is_primary=TRUE)

#### Scenario: Snapshot specific camera
- **WHEN** `GET /tents/{tent_id}/camera-snapshot?camera_id={uuid}` is called
- **THEN** the system SHALL return a snapshot from the specified camera

### Requirement: Camera Grid View
The frontend SHALL display multiple cameras in a grid layout (2x2 for 2-4 cameras, 3x3 for 5-9 cameras) with live thumbnail refresh.

#### Scenario: Grid view on tent detail
- **WHEN** a user views a tent that has multiple cameras configured
- **THEN** the system SHALL display all cameras in a responsive grid
- **AND** each thumbnail SHALL auto-refresh on a configurable interval (default: 30 seconds)

#### Scenario: Full-screen single camera
- **WHEN** a user taps a camera in the grid
- **THEN** the system SHALL display that camera full-screen with a manual refresh button

### Requirement: Camera Carousel on Mobile
On mobile viewports, the system SHALL display cameras in a horizontal swipeable carousel instead of a grid when there are 3+ cameras.

#### Scenario: Swipe between cameras
- **WHEN** a mobile user views a tent with multiple cameras
- **THEN** the system SHALL display cameras in a swipeable carousel with dot indicators
- **AND** the primary camera SHALL be shown first

### Requirement: AI Health Check Camera Selection
The AI health check feature SHALL allow users to select which camera(s) to include in the analysis when a tent has multiple cameras.

#### Scenario: Select camera for health check
- **WHEN** a user initiates an AI health check and the tent has multiple cameras
- **THEN** the system SHALL present a camera selector (checkboxes)
- **AND** submit selected camera snapshots to the AI for analysis

### Requirement: Migration from Single Camera URL
The system SHALL migrate existing `tents.camera_url` data to the new `tent_cameras` table and drop the `camera_url` column.

#### Scenario: Existing cameras are migrated
- **WHEN** migration 0025 runs
- **THEN** for each tent with a non-null `camera_url`, a `tent_cameras` record SHALL be created with `is_primary=TRUE`, `label='Camera'`, and `camera_type='http_snapshot'`
- **AND** the `tents.camera_url` column SHALL be dropped
