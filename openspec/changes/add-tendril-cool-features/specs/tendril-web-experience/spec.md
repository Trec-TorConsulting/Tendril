## ADDED Requirements

### Requirement: Command Palette
The system SHALL provide a global command palette accessible via ⌘K (macOS) or Ctrl+K (other platforms) from any dashboard page. The palette SHALL support fuzzy search across pages, grows, tents, strains, and devices. The palette SHALL support quick actions including creating resources and toggling theme.

#### Scenario: Open command palette
- **WHEN** user presses ⌘K on any dashboard page
- **THEN** a centered modal command palette appears with a search input focused
- **AND** recent items are shown by default

#### Scenario: Search and navigate
- **WHEN** user types a search query in the command palette
- **THEN** matching pages, grows, tents, strains, and devices are shown with fuzzy matching
- **AND** selecting a result navigates to that resource

#### Scenario: Quick action
- **WHEN** user selects a quick action (e.g., "Create Grow")
- **THEN** the relevant creation dialog or page opens

### Requirement: Celebration Animations
The system SHALL display confetti animations when users achieve milestones including grow completion, harvest creation, task completion streaks, and onboarding completion.

#### Scenario: Grow completion celebration
- **WHEN** a grow transitions to "completed" status
- **THEN** a confetti burst animation plays on screen

#### Scenario: Onboarding completion celebration
- **WHEN** user completes all onboarding checklist items
- **THEN** a confetti animation plays

### Requirement: Sparkline Mini-Charts
The system SHALL display inline sparkline charts on dashboard stat cards showing 7-day trends for pH, EC, temperature, and humidity readings.

#### Scenario: Dashboard sparklines
- **WHEN** user views the dashboard with active sensor data
- **THEN** each stat card displays a small sparkline showing the 7-day trend
- **AND** the sparkline color indicates stability (green), drift (yellow), or out-of-range (red)

### Requirement: Heat Map Calendar
The system SHALL display a GitHub-style activity heat map on the analytics page showing daily grow activity intensity across the year.

#### Scenario: View activity heat map
- **WHEN** user visits the analytics page
- **THEN** a calendar grid displays with color-coded squares representing daily activity levels
- **AND** hovering a square shows a tooltip with activity breakdown

### Requirement: Real-time Sensor Gauges
The system SHALL display animated radial gauge components for sensor readings (pH, EC, temperature, humidity) with color-coded zones indicating danger, warning, and optimal ranges.

#### Scenario: View sensor gauges
- **WHEN** user views a grow detail or tent detail page with sensor data
- **THEN** animated radial gauges display current values with color-coded arcs
- **AND** gauge values animate smoothly when data updates

### Requirement: Grow Timeline
The system SHALL display a vertical visual timeline on grow detail pages showing lifecycle milestones with linked journal entries, photos, and feeding events.

#### Scenario: View grow timeline
- **WHEN** user views a grow detail page
- **THEN** a vertical timeline shows milestones (planted, transplant, veg, flower, harvest) in chronological order
- **AND** journal entries, photos, and feedings appear at their corresponding dates

### Requirement: AI Chat Panel
The system SHALL provide a sliding chat panel accessible from any dashboard page for real-time AI conversation via WebSocket. The chat SHALL support streaming responses, markdown rendering, and context-aware prompts.

#### Scenario: Open AI chat
- **WHEN** user clicks the AI chat floating action button
- **THEN** a sliding drawer opens with a chat interface
- **AND** a WebSocket connection is established to the AI endpoint

#### Scenario: Send message and receive streaming response
- **WHEN** user sends a chat message
- **THEN** the AI response streams in progressively with a typing indicator
- **AND** the response renders markdown formatting

### Requirement: Photo Timelapse Player
The system SHALL provide a timelapse player on grow detail pages that allows scrubbing through grow photos chronologically with play/pause, speed control, and fullscreen capabilities.

#### Scenario: Play timelapse
- **WHEN** user opens the timelapse player on a grow with photos
- **THEN** photos display sequentially with smooth crossfade transitions
- **AND** a scrubber allows manual navigation through the photo timeline

### Requirement: Animated Grow Stage Indicator
The system SHALL display an animated plant illustration that visually represents the current grow stage, evolving from seed through harvest with smooth transitions.

#### Scenario: View grow stage indicator
- **WHEN** user views a grow detail page or dashboard active-grows widget
- **THEN** a plant illustration matches the current grow stage
- **AND** stage transitions animate with growth/morph effects

### Requirement: Live Camera Feeds
The system SHALL embed live camera streams from Frigate (via go2rtc) on tent detail pages, with WebRTC as primary transport and fallback to MSE and snapshot JPEG.

#### Scenario: View live camera feed
- **WHEN** user views a tent detail page with an associated camera
- **THEN** a live video feed displays from the tent's camera
- **AND** if WebRTC fails, the system falls back to MSE, then to periodic JPEG snapshots

### Requirement: Push Notifications
The system SHALL support PWA push notifications for sensor threshold alerts, task reminders, harvest countdowns, and AI health check results. Notification permission SHALL be requested after a meaningful user action, not on first visit.

#### Scenario: Receive push notification
- **WHEN** a sensor reading exceeds a configured threshold
- **THEN** the user receives a native push notification on their device
- **AND** tapping the notification navigates to the relevant resource

#### Scenario: Configure notification preferences
- **WHEN** user visits notification settings
- **THEN** they can enable/disable notification categories (sensor alerts, tasks, harvest, AI)
