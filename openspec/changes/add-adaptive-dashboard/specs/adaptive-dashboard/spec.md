# Capability: Adaptive Dashboard

## Purpose
A situational surfacing layer for the dashboard home that reorders and prioritizes content based on the grow's current stage, urgency of alerts/tasks/coaching, and sensor state — so the most important information and action appear first. Operates on top of, and without replacing, the user's persona-based layout mode.

## ADDED Requirements

### Requirement: Situational Section Ordering
The system SHALL order dashboard sections by a deterministic priority computed from the grow's stage, active alerts, coaching, pending tasks, and sensor state.

#### Scenario: Critical alert pinned to top
- **WHEN** an active critical alert exists for the selected grow
- **THEN** the dashboard surfaces the alert-related content at the top

#### Scenario: Stage-relevant boosting
- **WHEN** the selected grow is in ripening or harvesting
- **THEN** harvest/trichome guidance is boosted toward the top
- **AND** when the grow is in seedling or vegetative, harvest countdown is de-prioritized

#### Scenario: Fallback to fixed order
- **WHEN** no prioritized items are present
- **THEN** the dashboard renders the existing default section order

### Requirement: Next Best Action Block
The system SHALL display a single Next Best Action block selecting the most important actionable item.

#### Scenario: Highest-priority action selected
- **WHEN** multiple actionable items exist (critical alert, urgent task, important coaching)
- **THEN** the Next Best Action shows the critical alert first, following the documented priority order
- **AND** provides a one-tap action for it

#### Scenario: Calm empty state
- **WHEN** no urgent actionable items exist
- **THEN** the Next Best Action shows a positive status and the time until the next routine check

### Requirement: Persona Layout Preservation
The system SHALL apply situational ordering within the user's selected persona layout mode without changing its density, tabs, or navigation.

#### Scenario: Ordering respects persona
- **WHEN** situational ordering is applied
- **THEN** the persona layout's density and navigation remain unchanged
