## ADDED Requirements

### Requirement: Integration Action Control Policies
The system SHALL enforce tenant-scoped control policies for AI-initiated integration actions.

#### Scenario: Allowed action executes
- **WHEN** an AI action targets an integration operation that is allowlisted for the tenant and mapped device scope
- **THEN** the action may proceed to approval/execution stages

#### Scenario: Disallowed action blocked
- **WHEN** an AI action targets an operation denied by tenant policy
- **THEN** the system blocks execution and records the policy reason

### Requirement: Risk-Tiered Execution Controls
The system SHALL classify integration operations by risk tier and enforce controls accordingly.

#### Scenario: Low-risk operation
- **WHEN** an action is classified as low risk by policy
- **THEN** execution may proceed according to tenant approval rules

#### Scenario: High-risk operation requires simulation
- **WHEN** an action is classified as high risk
- **THEN** the system requires dry-run/simulation output before approval and execution

#### Scenario: High-risk default for outbound control commands
- **WHEN** an action is an outbound device control command
- **THEN** the system classifies it as high risk by default
- **AND** requires explicit approval and simulation before execution

### Requirement: Connector Coverage for Control Policies
The system SHALL enforce integration action controls for all supported connectors, including Pulse, OpenWeather, and Ecowitt.

#### Scenario: Connector policy enforcement
- **WHEN** an AI action targets any supported connector operation
- **THEN** the same policy, approval, and audit controls are applied consistently

### Requirement: Integration Action Auditability
The system SHALL record immutable audit entries for AI-initiated integration actions.

#### Scenario: Action audit record created
- **WHEN** an integration action is proposed, approved, executed, verified, or blocked
- **THEN** the system writes an audit entry with tenant, integration, operation, actor, outcome, and timestamp

### Requirement: Idempotent Integration Command Execution
The system SHALL execute integration commands with idempotency keys to prevent duplicate side effects.

#### Scenario: Duplicate command prevented
- **WHEN** the same action is retried due to transient errors
- **THEN** the system reuses the action idempotency key and prevents duplicate side effects in external systems where supported
- **AND** records retry attempts and final outcome
