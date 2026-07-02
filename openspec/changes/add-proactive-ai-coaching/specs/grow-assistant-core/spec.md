## ADDED Requirements

### Requirement: Proactive Coaching Triggers
The system SHALL evaluate each active grow on a periodic cadence and generate coaching only when a deterministic trigger fires (stage transition, new grow week, sustained sensor drift, or pre-emergency composite condition).

#### Scenario: Stage transition coaching
- **WHEN** a grow transitions from vegetative to flowering
- **THEN** the system generates a quality-first coaching message about the transition (e.g., environment and VPD guidance)

#### Scenario: Pre-emergency nudge before an alert
- **WHEN** water temperature is rising and dissolved oxygen is falling but neither has crossed the critical alert threshold
- **THEN** the system generates an early root-health coaching nudge

#### Scenario: No trigger, no coaching
- **WHEN** no coaching trigger condition is met for a grow
- **THEN** the system does not generate a coaching message and makes no LLM call

### Requirement: Coaching Message Generation with Caching and Fallback
The system SHALL generate coaching messages using a local provider first with hosted fallback, and SHALL cache and de-duplicate messages per grow and topic.

#### Scenario: Cached message reused
- **WHEN** a coaching topic fires with the same inputs as a recently generated message
- **THEN** the system reuses the cached message without invoking an LLM

#### Scenario: De-duplication within cooldown
- **WHEN** a coaching topic for a grow already fired within its cooldown window and severity is not critical
- **THEN** the system does not emit a duplicate coaching event

#### Scenario: Critical bypasses cooldown
- **WHEN** a critical-severity coaching condition occurs during a cooldown window
- **THEN** the system still emits the coaching event

### Requirement: Coaching Delivery and Consent
The system SHALL always create an in-app coaching event and SHALL send web push only for important or critical severity, honoring per-tenant notification preferences and a proactive-coaching consent toggle.

#### Scenario: In-app plus push for important events
- **WHEN** an important-severity coaching event is created and the tenant allows push
- **THEN** the system records the in-app event and dispatches a web push notification

#### Scenario: Coaching disabled by user
- **WHEN** proactive coaching is disabled for a grow or tenant
- **THEN** the system does not generate coaching events for that scope, except critical safety events

#### Scenario: Acknowledge and dismiss
- **WHEN** a user acknowledges or dismisses a coaching event
- **THEN** the system records the action and stops surfacing that event prominently
