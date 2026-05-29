## ADDED Requirements

### Requirement: Layout Mode Selection
The system SHALL provide 5 selectable layout modes: Beginner, Home, Standard, Pro, and Commercial. Each mode SHALL control information density, navigation structure, and component composition for the authenticated user.

#### Scenario: User selects layout mode during onboarding
- **WHEN** a new user completes the onboarding wizard
- **THEN** the system SHALL set their `layout_mode` based on their answers (grow count + experience level)
- **AND** the dashboard SHALL immediately render in the selected mode

#### Scenario: User changes layout mode in settings
- **WHEN** a user navigates to Settings > Layout and selects a different mode
- **THEN** the system SHALL update their `layout_mode` via `PATCH /v1/auth/profile`
- **AND** the UI SHALL re-render without page reload using the new mode configuration

### Requirement: Layout Mode Persistence
The system SHALL persist the user's layout mode in the `users.layout_mode` database column and include it in the `/v1/auth/me` response.

#### Scenario: Layout mode survives session
- **WHEN** a user logs out and logs back in
- **THEN** their previously selected layout mode SHALL be restored

### Requirement: Grow-Centric Home Screen
Each layout mode SHALL render a home screen where the primary focus is the user's active grow cycle(s). The grow SHALL be the top-level navigational entity.

#### Scenario: Beginner mode home screen
- **WHEN** a user in Beginner mode opens the app
- **THEN** the system SHALL display a full-screen single-grow card with guided next-steps and achievements

#### Scenario: Home mode home screen
- **WHEN** a user in Home mode opens the app
- **THEN** the system SHALL display a hero grow card with sensor summary, harvest countdown, and quick-action buttons

#### Scenario: Standard mode home screen
- **WHEN** a user in Standard mode opens the app
- **THEN** the system SHALL display a multi-grow grid with stats strip and recent activity feed

#### Scenario: Pro mode home screen
- **WHEN** a user in Pro mode opens the app
- **THEN** the system SHALL display a dense multi-grow table with live sensor panels and alerts sidebar

#### Scenario: Commercial mode home screen
- **WHEN** a user in Commercial mode opens the app
- **THEN** the system SHALL display a fleet overview with team activity feed, alert banner, and multi-tenant summary

### Requirement: Mobile Bottom Tab Navigation
On mobile viewports (< 768px), the system SHALL render a bottom tab bar for primary navigation instead of a sidebar. The tab configuration SHALL vary by layout mode.

#### Scenario: Bottom tabs render on mobile
- **WHEN** a user accesses the app on a mobile device
- **THEN** the system SHALL display a bottom tab bar with mode-specific tabs
- **AND** the sidebar SHALL be hidden (accessible only via hamburger menu if needed)

#### Scenario: Log tab is always present
- **WHEN** any layout mode is active on mobile
- **THEN** the bottom tab bar SHALL include a "Log" tab in position 2 or 3
- **AND** tapping it SHALL open the Quick-Log sheet

### Requirement: Desktop Layout Adaptation
On desktop viewports (≥ 1024px), the system SHALL render a sidebar navigation with content density matching the selected layout mode.

#### Scenario: Desktop sidebar adapts to mode
- **WHEN** a user in Pro mode accesses the app on desktop
- **THEN** the sidebar SHALL show all navigation items without collapsing
- **AND** the content area SHALL use dense, multi-panel layouts

#### Scenario: Desktop beginner mode simplifies sidebar
- **WHEN** a user in Beginner mode accesses the app on desktop
- **THEN** the sidebar SHALL show only essential items (Home, My Grow, Log, Camera, Guide)
- **AND** advanced features SHALL be hidden or shown as locked teasers

### Requirement: Onboarding Wizard
The system SHALL present a 3-step onboarding wizard to new users (users with 0 grows) that determines their layout mode and creates their first grow.

#### Scenario: New user sees onboarding
- **WHEN** a user logs in for the first time and has 0 grows
- **THEN** the system SHALL display the onboarding wizard instead of the dashboard

#### Scenario: Wizard completes in under 30 seconds
- **WHEN** a user progresses through all 3 wizard steps
- **THEN** the total interaction time SHALL be under 30 seconds for a typical user
- **AND** the wizard SHALL set their layout mode and optionally create their first grow

### Requirement: Mode Upgrade Suggestions
The system SHALL suggest a layout mode upgrade when user behavior outgrows their current mode.

#### Scenario: Beginner outgrows mode
- **WHEN** a Beginner-mode user creates their 2nd grow or 5th bucket
- **THEN** the system SHALL display a non-intrusive prompt suggesting Home or Standard mode
- **AND** the user SHALL be able to dismiss or accept the suggestion

### Requirement: Layout Mode Configuration
Each layout mode SHALL be defined as a configuration object controlling: visible components, component order, information density level (minimal/low/medium/high/very-high), navigation tabs, and animation style.

#### Scenario: Mode configuration drives rendering
- **WHEN** the LayoutEngine reads the active mode configuration
- **THEN** it SHALL render only the components listed in that mode's config
- **AND** components SHALL receive density props from the configuration
