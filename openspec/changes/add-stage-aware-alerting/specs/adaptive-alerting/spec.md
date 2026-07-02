# Capability: Adaptive Alerting

## Purpose
Dynamic, context-aware alerting for grow environments. Thresholds and alert messaging adapt to the grow's current stage and strain rather than using fixed values, aligning with Tendril's cannabis quality-first philosophy (quality over yield). Seeded from documented science defaults and overridable per grow.

## ADDED Requirements

### Requirement: Stage-Aware Threshold Resolution
The system SHALL resolve effective sensor thresholds at evaluation time based on the grow's current stage, seeded from documented science defaults.

#### Scenario: EC threshold differs by stage
- **WHEN** the automation engine evaluates EC for a grow in the vegetative stage
- **THEN** it uses the vegetative EC range
- **AND** when the same grow is in late flowering, it uses the lower late-flower EC range

#### Scenario: Fallback preserves existing behavior
- **WHEN** no stage-specific default or override exists for a metric
- **THEN** the engine uses the existing static grow-type default without error

#### Scenario: Late-flower derivation
- **WHEN** a grow is in the flowering stage beyond the configured late-flower week cutoff
- **THEN** the engine resolves thresholds using the late-flowering ranges

### Requirement: Per-Grow Threshold Overrides
The system SHALL allow users to override sensor thresholds per grow and per stage, taking precedence over science defaults.

#### Scenario: Override takes precedence
- **WHEN** a per-grow override exists for a metric and the grow's current stage
- **THEN** the engine uses the override values instead of the science default

#### Scenario: Stage-agnostic override
- **WHEN** a per-grow override exists for a metric with no stage specified
- **THEN** the engine applies it across all stages unless a more specific stage override exists

#### Scenario: Reset to default
- **WHEN** a user deletes an override for a metric/stage
- **THEN** the engine reverts to the science default for that metric/stage

### Requirement: Contextual Actionable Alert Messaging
The system SHALL include stage, current value, effective range, and a quality-first recommendation in alert payloads without invoking an LLM.

#### Scenario: Actionable alert copy
- **WHEN** a stage-aware threshold is breached
- **THEN** the alert message states the current value, the effective range for the current stage, and a recommended corrective action prioritizing plant quality

### Requirement: Cooldown Reset on Stage Transition
The system SHALL clear alert cooldowns for rules whose effective threshold changed when a grow transitions stage.

#### Scenario: New alert fires after stage change
- **WHEN** a grow transitions to a stage where a previously-suppressed condition is now out of range
- **THEN** the affected rule's cooldown is cleared so the alert can fire on the next evaluation
