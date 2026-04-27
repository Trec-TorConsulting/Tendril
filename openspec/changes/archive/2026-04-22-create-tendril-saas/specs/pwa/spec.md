## ADDED Requirements

### Requirement: Installable PWA
The system SHALL be a Progressive Web App that is installable on mobile and desktop devices.

#### Scenario: Add to home screen
- **WHEN** a user visits Tendril on a mobile browser
- **THEN** the browser prompts to install the app and it launches in standalone mode with custom icons and splash screen

### Requirement: Offline Shell
The system SHALL cache the application shell and static assets for offline access via a service worker.

#### Scenario: Offline dashboard access
- **WHEN** a user opens Tendril while offline
- **THEN** the cached dashboard shell loads with the last-known data and a banner indicating offline status

### Requirement: Web Push Notifications
The system SHALL support Web Push notifications for sensor alerts, health check results, and grow events.

#### Scenario: Push notification for pH alert
- **WHEN** a bucket's pH reading exceeds the configured threshold
- **THEN** users with push notifications enabled receive a push notification on their device

#### Scenario: Push permission prompt
- **WHEN** a user enables notifications in settings
- **THEN** the browser prompts for push notification permission and the subscription is stored server-side

### Requirement: Background Sync
The system SHALL queue data submissions made while offline and sync them when connectivity is restored.

#### Scenario: Offline journal entry
- **WHEN** a user adds a journal entry while offline
- **THEN** the entry is queued locally and automatically synced to the server when the device reconnects

### Requirement: Web App Manifest
The system SHALL provide a valid web app manifest with name, icons, theme color, background color, and display mode.

#### Scenario: Manifest validation
- **WHEN** the manifest.json is loaded
- **THEN** it contains all required fields for Lighthouse PWA audit compliance
