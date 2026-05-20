## ADDED Requirements

### Requirement: Unified Settings Navigation
The system SHALL organize all user-facing settings into a maximum of 4 logical sidebar groups: Account, Automation, Connections, and Library.

#### Scenario: User navigates to account settings
- **WHEN** user clicks "Account" in the sidebar
- **THEN** the system displays sub-items: Profile, Security, Billing, Team

#### Scenario: User navigates to automation settings
- **WHEN** user clicks "Automation" in the sidebar
- **THEN** the system displays sub-items: Rules, Schedules, Notifications

#### Scenario: User navigates to connections
- **WHEN** user clicks "Connections" in the sidebar
- **THEN** the system displays sub-items: Devices, Integrations

### Requirement: Settings Hub with Search
The system SHALL provide a settings index page that displays all settings categories as navigable cards with a keyword search/filter.

#### Scenario: User searches for a setting
- **WHEN** user types "notifications" in the settings search field
- **THEN** the system highlights or filters to show the Notifications settings card

#### Scenario: User opens settings hub
- **WHEN** user navigates to the settings hub page
- **THEN** the system displays categorized cards linking to: Profile, Security, Billing, Team, Notifications, Automation Rules, Schedules, Devices, Integrations, API Keys

### Requirement: No Duplicate Entry Points
The system SHALL NOT expose the same settings page from more than one navigation path without a redirect.

#### Scenario: Old billing route redirects
- **WHEN** user navigates to `/dashboard/billing` directly
- **THEN** the system redirects to `/dashboard/settings/account` billing section

## REMOVED Requirements

### Requirement: Standalone Billing Page
**Reason**: Billing is consolidated under Account settings to eliminate duplicate access points.
**Migration**: `/dashboard/billing` redirects to `/dashboard/settings/account`.
