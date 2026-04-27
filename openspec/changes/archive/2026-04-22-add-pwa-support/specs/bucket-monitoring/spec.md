## ADDED Requirements

### Requirement: Background Sync for Sensor Readings
The system SHALL queue manual sensor readings in IndexedDB when the device is offline and automatically replay them to the server when connectivity resumes.

#### Scenario: Offline sensor entry
- **WHEN** a user submits a manual sensor reading while offline
- **THEN** the reading is stored in IndexedDB and a background sync is registered

#### Scenario: Sync on reconnect
- **WHEN** network connectivity resumes after offline sensor entries were queued
- **THEN** the service worker replays all queued readings to `POST /api/buckets/{id}/sensors`
- **AND** a confirmation toast is shown to the user
