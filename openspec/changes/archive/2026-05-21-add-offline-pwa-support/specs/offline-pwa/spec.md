## ADDED Requirements

### Requirement: Offline PWA Functionality
The system SHALL function in offline mode for core operations: viewing grow data, browsing grow type configs, and queuing data entries for sync when connectivity returns.

#### Scenario: Grower in basement grow room with no signal
- **WHEN** a grower opens Tendril PWA without internet connectivity
- **THEN** the app loads from cache, displays last-synced grow data, allows browsing grow type configs and stage guidance, and queues any new entries (sensor readings, notes, expenses) for background sync when connectivity returns

### Requirement: Background Sync
The system SHALL queue offline data entries and automatically sync them when connectivity is restored, with visual indication of pending sync items.

#### Scenario: Connectivity returns after offline session
- **WHEN** the device regains internet connectivity after an offline session
- **THEN** all queued entries sync automatically in the background, the pending sync counter decreases to zero, and the grower receives confirmation that all data has been synced
