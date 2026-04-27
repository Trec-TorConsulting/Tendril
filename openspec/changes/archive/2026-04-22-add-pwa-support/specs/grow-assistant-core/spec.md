## ADDED Requirements

### Requirement: PWA Manifest and Installability
The system SHALL serve a valid Web App Manifest (`manifest.json`) and register a service worker so the application is installable on mobile and desktop devices.

#### Scenario: Install prompt on mobile
- **WHEN** a user visits the app in a mobile browser that supports PWA
- **THEN** the browser's install prompt is triggered (or a custom install banner is shown)

#### Scenario: Installed app launches standalone
- **WHEN** a user launches the installed PWA from their home screen
- **THEN** the app opens in standalone mode (no browser chrome) with the configured theme color and splash screen

---

### Requirement: Offline App Shell
The system SHALL cache the app shell (HTML, CSS, JS, icons) via a service worker so the UI loads even without network connectivity.

#### Scenario: Offline load
- **WHEN** the device has no network connectivity
- **THEN** the cached app shell loads and displays a graceful offline state for API-dependent sections

#### Scenario: Cache update
- **WHEN** a new version of the app is deployed and the user opens the app
- **THEN** the service worker fetches updated assets and activates the new cache
