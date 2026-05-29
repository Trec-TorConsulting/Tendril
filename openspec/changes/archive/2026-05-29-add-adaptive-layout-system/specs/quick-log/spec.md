## ADDED Requirements

### Requirement: Quick-Log Accessibility
The Quick-Log system SHALL be accessible within 2 taps from any screen in the application. It SHALL be triggered via the bottom tab "Log" button on mobile, ⌘L keyboard shortcut on desktop, or the FAB in applicable modes.

#### Scenario: Quick-log from bottom tab
- **WHEN** a user taps the "Log" tab in the bottom navigation
- **THEN** a bottom sheet SHALL appear with quick-log action options (Feed, Photo, Note, Reading)

#### Scenario: Quick-log via keyboard shortcut
- **WHEN** a user presses ⌘L (Mac) or Ctrl+L (Windows) on desktop
- **THEN** the Quick-Log modal SHALL open with the feeding form pre-selected

### Requirement: Feeding Log with Bulk Bucket Support
The Quick-Log feeding form SHALL support logging identical readings across multiple buckets simultaneously for DWC flush-and-fill operations.

#### Scenario: Single bucket feeding log
- **WHEN** a user selects one bucket and enters pH, EC, water temperature, and volume
- **THEN** the system SHALL create a feeding record for that bucket via `POST /v1/quick-log/feeding`

#### Scenario: Bulk bucket feeding log (DWC flush-and-fill)
- **WHEN** a user selects multiple buckets (e.g., "All DWC buckets in Tent A") and enters shared readings
- **THEN** the system SHALL create identical feeding records for all selected buckets in a single API call
- **AND** display a confirmation showing how many buckets were logged

#### Scenario: Nutrient selection in feeding log
- **WHEN** a user logs a feeding
- **THEN** the system SHALL provide a nutrient product selector with the user's recent/saved products
- **AND** allow specifying dose amounts per product

### Requirement: Quick-Log Feeding API
The system SHALL provide `POST /v1/quick-log/feeding` accepting an array of bucket IDs and shared measurement data.

#### Scenario: Bulk feeding API call
- **WHEN** `POST /v1/quick-log/feeding` is called with `{"bucket_ids": [...], "ph": 5.8, "ec": 1.2, "water_temp_f": 68, "volume_gal": 5, "nutrients": [...]}`
- **THEN** the system SHALL create one feeding record per bucket_id with the shared measurement data
- **AND** return a summary of created records

### Requirement: Quick Photo with Auto-Tag
The Quick-Log photo feature SHALL open the device camera and automatically associate the captured photo with the user's active grow context.

#### Scenario: Quick photo capture
- **WHEN** a user taps "Photo" in the Quick-Log sheet
- **THEN** the device camera SHALL activate
- **AND** the captured photo SHALL be tagged to the currently selected grow/bucket
- **AND** uploaded via `POST /v1/quick-log/photo`

### Requirement: Quick Note with Tags
The Quick-Log note feature SHALL provide a minimal text input with quick-tag buttons for common observations.

#### Scenario: Quick note with tag
- **WHEN** a user taps "Note" and selects the "Topped" tag + optional free text
- **THEN** the system SHALL create a journal entry with the tag and text via `POST /v1/quick-log/note`
- **AND** associate it with the active grow

#### Scenario: Available quick-tags
- **WHEN** the quick note form renders
- **THEN** the system SHALL display common tags: "Topped", "Transplanted", "Pest Spotted", "Defoliated", "Flushed", "Flipped to 12/12", "Harvested", "Training", "Pruned"

### Requirement: Manual Environment Reading
The Quick-Log system SHALL allow users to manually log environment readings when sensors are not connected.

#### Scenario: Manual tent reading
- **WHEN** a user selects "Reading" and enters temperature, humidity, and optionally VPD
- **THEN** the system SHALL create a tent sensor reading via `POST /v1/quick-log/reading`
- **AND** the reading SHALL be tagged as `source='manual'`

### Requirement: Offline Queue
The Quick-Log system SHALL queue actions locally when the device is offline and automatically sync when connectivity is restored.

#### Scenario: Offline logging
- **WHEN** a user submits a quick-log action while offline
- **THEN** the system SHALL store the action in localStorage with a client-generated timestamp
- **AND** display a visual indicator that the action is queued

#### Scenario: Offline queue sync
- **WHEN** network connectivity is restored
- **THEN** the system SHALL replay all queued actions via `POST /v1/quick-log/batch`
- **AND** remove successfully synced items from the local queue
- **AND** display a notification showing how many items were synced

### Requirement: Recent Values Quick-Fill
The feeding log form SHALL display the user's most recent values as quick-fill suggestions to speed up repeat logging.

#### Scenario: Recent pH suggestion
- **WHEN** a user opens the feeding form for a bucket they've previously logged
- **THEN** the system SHALL display their last pH, EC, and volume values as tap-to-fill suggestions
- **AND** the user SHALL be able to accept (tap) or override (type) these values

### Requirement: Quick-Log Batch Replay API
The system SHALL provide `POST /v1/quick-log/batch` for replaying queued offline actions.

#### Scenario: Batch replay
- **WHEN** `POST /v1/quick-log/batch` is called with an array of quick-log actions (each with type, data, and client_timestamp)
- **THEN** the system SHALL process each action in order
- **AND** return a summary of successes and failures
- **AND** use `client_timestamp` as the action timestamp (not server receive time)
