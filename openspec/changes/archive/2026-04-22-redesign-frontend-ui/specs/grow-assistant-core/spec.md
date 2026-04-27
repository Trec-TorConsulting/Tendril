## MODIFIED Requirements

### Requirement: Frontend Navigation
The system SHALL provide a bottom navigation bar (mobile) and sidebar (desktop) with 5 primary views: Dashboard, Grows, Buckets, Analytics, and Chat. Navigation SHALL use hash-based routing (`#view` / `#view/id`) supporting browser back/forward. The currently active tent SHALL be selectable via a header dropdown, persisted in localStorage.

#### Scenario: User navigates between views
- **WHEN** user taps a nav item (e.g., Buckets)
- **THEN** the URL hash updates to `#buckets` and the Buckets view renders in the main content area
- **AND** the nav item shows as active

#### Scenario: User navigates directly via URL
- **WHEN** user loads the app with `#grows/3` in the URL
- **THEN** the Grow detail view renders for grow ID 3

#### Scenario: User switches active tent
- **WHEN** user selects a different tent from the header dropdown
- **THEN** all views refresh to show data for the selected tent
- **AND** the selection persists across page refreshes

### Requirement: Dashboard Overview
The system SHALL display a Dashboard view as the default landing page showing: grow score card with factor breakdown, environment snapshot (temp/humidity/VPD), active alerts with severity badges, recent activity feed (last 10 events), camera snapshot, and active grow summary.

#### Scenario: Dashboard loads with active grow
- **WHEN** user navigates to `#dashboard`
- **THEN** the grow score card shows the current score with colored indicator
- **AND** active alerts are listed with dismiss buttons
- **AND** the camera snapshot shows the latest image

### Requirement: Grow Manager
The system SHALL provide a Grow Manager view at `#grows` showing active grows with live bucket data and archived grows with snapshot data. Active grows SHALL display current bucket sensors, journal entries, and photos in real-time. The system SHALL support starting, archiving, comparing, and annotating grows.

#### Scenario: User views active grow
- **WHEN** user clicks an active grow
- **THEN** the detail view shows live bucket data (latest sensors, journal, photos) from the grow's start date to now

#### Scenario: User views archived grow
- **WHEN** user clicks an archived grow
- **THEN** the detail view shows the bucket snapshot captured at archive time

### Requirement: Bucket Detail Tabs
The system SHALL display bucket details in a tabbed layout with six tabs: Overview, Sensors, Diary, Photos, Feeding, and Pump. Each tab SHALL be independently scrollable and load data on activation.

#### Scenario: User opens bucket detail
- **WHEN** user clicks a bucket card
- **THEN** the bucket detail view opens at `#buckets/{id}` with the Overview tab active

#### Scenario: User switches bucket tabs
- **WHEN** user taps the Sensors tab
- **THEN** sensor charts and drift analysis render without affecting other tabs

### Requirement: Modular Frontend Architecture
The system SHALL split the frontend into separate CSS and JS files loaded via standard `<script>` tags. All JS files SHALL share state through a global `App` namespace. The service worker SHALL cache all static assets for offline access.

#### Scenario: App loads with cached assets
- **WHEN** user opens the app while offline
- **THEN** the HTML shell, CSS, and all JS files load from service worker cache
- **AND** API calls show graceful offline error messages
