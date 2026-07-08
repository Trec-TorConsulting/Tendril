# Capability: Adaptive Experience

## Purpose
Adaptive onboarding and navigation surfaces. Onboarding progresses with the user's demonstrated competence rather than a fixed one-time flow, and the command palette ranks results by recency/frequency and suggests contextual actions based on the selected grow's stage and state.

## ADDED Requirements

### Requirement: Progressive Onboarding by Milestone
The system SHALL model onboarding as milestone progression and advance layout complexity as the user completes real actions, while allowing manual override.

#### Scenario: Next step surfaced
- **WHEN** a user has created a tent but no grow
- **THEN** the onboarding surface shows creating a grow as the next recommended step

#### Scenario: Layout advances with competence
- **WHEN** a user completes early milestones (tent, grow, device, first log)
- **THEN** the system may advance the layout from beginner toward standard
- **AND** a manual layout choice in settings overrides automatic advancement

#### Scenario: Re-engagement after inactivity
- **WHEN** a user returns after a period of inactivity with incomplete milestones
- **THEN** the system re-surfaces the recommended next step

### Requirement: Recency- and Frequency-Ranked Palette
The system SHALL rank command palette results by combined recency and frequency while preserving exact-match search.

#### Scenario: Frequently used items rank higher
- **WHEN** a user opens the command palette
- **THEN** items the user visits often and recently appear before rarely used items

#### Scenario: Selected grow entities boosted
- **WHEN** a grow is selected
- **THEN** its related tent, devices, and strains are boosted toward the top of results

### Requirement: Contextual Action Suggestions
The system SHALL suggest contextual actions in the command palette based on the selected grow's stage and state.

#### Scenario: Harvest actions in flower
- **WHEN** the selected grow is in flowering or ripening
- **THEN** the palette suggests relevant actions such as running a health check or logging trichomes

#### Scenario: Suggestions hidden when irrelevant
- **WHEN** the selected grow is in an early vegetative stage
- **THEN** harvest-related suggestions are not shown
