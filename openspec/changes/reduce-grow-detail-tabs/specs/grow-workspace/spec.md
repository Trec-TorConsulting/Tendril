## ADDED Requirements

### Requirement: Consolidated Grow Detail Tabs
The system SHALL present the grow detail page with a maximum of 9 tabs for hydro/indoor grows, grouping related concerns into unified views.

#### Scenario: Hydro grow shows consolidated tabs
- **WHEN** user navigates to a hydro grow detail page (DWC, RDWC, NFT, etc.)
- **THEN** the system displays tabs: Overview, Buckets, Activity, Tasks, Nutrition & Yield, Health & Photos, Settings

#### Scenario: Outdoor grow shows field tab
- **WHEN** user navigates to an outdoor grow detail page
- **THEN** the system displays the standard tabs plus a "Field" tab containing Plot Designer, Soil Health, Runoff, Field Scout, Irrigation, and Season Timeline sub-sections

### Requirement: Activity Tab Unified Timeline
The system SHALL display an interleaved timeline of sensor readings and journal entries within the Activity tab, filterable by bucket and event type.

#### Scenario: User views activity timeline
- **WHEN** user opens the Activity tab
- **THEN** the system displays journal entries and sensor readings in reverse chronological order as a unified stream

#### Scenario: User filters activity by bucket
- **WHEN** user selects a specific bucket from the filter
- **THEN** the timeline shows only entries and readings for that bucket

#### Scenario: User switches to readings-only view
- **WHEN** user selects "Readings" sub-view within the Activity tab
- **THEN** the system displays the sensor chart view (previously the standalone Sensors tab)

### Requirement: Tab Badges
The system SHALL display count badges or indicator dots on tabs to surface actionable information without requiring tab navigation.

#### Scenario: Tasks tab shows open count
- **WHEN** the grow has 3 open tasks
- **THEN** the Tasks tab label displays "(3)" badge

#### Scenario: Health tab shows new issue indicator
- **WHEN** a new health issue has been detected since the user last viewed the Health tab
- **THEN** the Health & Photos tab displays a dot indicator
