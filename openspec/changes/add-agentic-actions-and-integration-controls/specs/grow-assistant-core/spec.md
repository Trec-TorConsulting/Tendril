## ADDED Requirements

### Requirement: Agent Action Lifecycle
The system SHALL execute actionable AI requests through an explicit lifecycle: observe, plan, propose, approve, execute, verify, and summarize.

#### Scenario: Plan generated before execution
- **WHEN** a user request implies a mutating action
- **THEN** the system creates a structured action plan with steps, confidence, and required approvals
- **AND** no mutating step executes before policy and approval checks pass

#### Scenario: Verification after execution
- **WHEN** an approved action is executed
- **THEN** the system runs verification checks for expected postconditions
- **AND** records verification status with evidence in the action record

### Requirement: Approval Gate for Mutating Actions
The system SHALL require explicit approval for AI-initiated mutating actions unless tenant policy permits auto-approval for that risk tier.

#### Scenario: Approval required
- **WHEN** an action is classified as mutating and requires approval by policy
- **THEN** the system marks it pending approval and does not execute it
- **AND** emits a status event for the UI

#### Scenario: Approval denied or expired
- **WHEN** an action is rejected or approval expires
- **THEN** the system marks the action as not executed
- **AND** stores the rejection/expiration reason in audit data

#### Scenario: Authorized approvers
- **WHEN** an action requires approval
- **THEN** only tenant admins and tenant members with the required approval permission can approve or reject it

### Requirement: Safe Auto-Approval Policy
The system SHALL auto-approve only actions explicitly classified as 100% safe.

#### Scenario: Auto-approved safe actions
- **WHEN** the agent proposes one of the safe actions (create task, create journal entry, generate checklist)
- **THEN** the action may auto-approve and proceed directly to execution and verification

#### Scenario: Non-safe actions require approval
- **WHEN** the agent proposes any mutating action outside the explicit safe list
- **THEN** the action remains pending approval and does not auto-execute

### Requirement: Health-Check-First Agentic Rollout
The system SHALL apply the full action lifecycle to health-check and health-check-derived actions first.

#### Scenario: Health check produces actionable plan
- **WHEN** a health check identifies issues requiring intervention
- **THEN** the system produces lifecycle-tracked actions with policy, approval, execution, and verification states

### Requirement: Conversation-Thread Binding in Chat
The system SHALL bind websocket chat to a stable conversation thread identifier that can be resumed across reconnects and navigation.

#### Scenario: Resume existing conversation
- **WHEN** a client reconnects with a valid conversation identifier
- **THEN** the system resumes that thread and appends new messages to it

#### Scenario: Start new conversation
- **WHEN** a client opens chat without a conversation identifier
- **THEN** the system creates a new conversation and returns its identifier to the client

### Requirement: Agent Observability Metrics
The system SHALL emit observability signals for agent safety and effectiveness.

#### Scenario: Action telemetry emitted
- **WHEN** an action proposal, approval, execution, verification, or policy block occurs
- **THEN** the system records structured telemetry for status, latency, and outcome

### Requirement: Approval and Action Notifications
The system SHALL notify users about pending approvals and action lifecycle changes across all configured delivery channels.

#### Scenario: Notification fanout
- **WHEN** an action enters pending approval or changes lifecycle state
- **THEN** notifications are sent via in-app, web push, and email channels

## MODIFIED Requirements

### Requirement: WebSocket Streaming
The system SHALL stream LLM responses via WebSocket with keepalive pings to prevent connection drops and preserve action lifecycle event delivery.

#### Scenario: Streaming response
- **WHEN** a user sends a message via the WebSocket endpoint `/ws/chat`
- **THEN** tokens are streamed incrementally as the LLM generates them

#### Scenario: Connection keepalive
- **WHEN** a WebSocket connection is idle during LLM processing
- **THEN** the server sends periodic keepalive pings to prevent timeout

#### Scenario: Lifecycle events during streaming
- **WHEN** the agent changes action lifecycle state (proposed, approved, executing, verified, blocked)
- **THEN** the server sends corresponding websocket events without interrupting token streaming
