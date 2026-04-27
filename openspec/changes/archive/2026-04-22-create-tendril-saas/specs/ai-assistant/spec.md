## ADDED Requirements

### Requirement: AI Chat
The system SHALL provide a WebSocket-based AI chat assistant per tenant, powered by Ollama.

#### Scenario: Chat message
- **WHEN** a user sends a message via WebSocket
- **THEN** the system streams an AI response with grow-aware context from the tenant's data

#### Scenario: Authentication
- **WHEN** a WebSocket connection is initiated
- **THEN** the system validates a ticket token before accepting the connection

### Requirement: Vision Health Check
The system SHALL perform AI-powered visual health assessments using camera snapshots, scoped per tenant.

#### Scenario: Manual health check
- **WHEN** a user triggers a health check for a tent
- **THEN** the system fetches a camera snapshot, injects the grow type profile's AI prompt context into the system prompt, sends it to the AI model, and stores the evaluation

#### Scenario: Grow-type-aware health check
- **WHEN** a health check runs for a tent with a specific grow type
- **THEN** the AI prompt includes grow-type-specific guidance (e.g., DWC: check root health, water clarity, air stone activity; Soil: check moisture, pests, top-dressing; NFT: check flow rate, root mat, channel drainage)
- **AND** the AI does NOT suggest actions irrelevant to the grow type (e.g., no "check your air stones" for soil grows)

#### Scenario: Scheduled health check
- **WHEN** the scheduler runs and a tent has an active grow
- **THEN** the system performs an automated health check every 12 hours

### Requirement: AI Coach Tips
The system SHALL generate contextual coaching tips based on the tenant's current grow data.

#### Scenario: Dashboard coach tip
- **WHEN** the dashboard loads
- **THEN** the system returns a fresh AI-generated tip relevant to the tenant's active grow type, growth stage, and sensor readings
- **AND** tips are contextual to the grow type (e.g., DWC: "Reservoir change due in 2 days", Coco: "CalMag reminder — feed with every watering", Kratky: "Water level looks good — don't top off")

### Requirement: AI Insights
The system SHALL provide on-demand AI analysis: harvest prediction, nutrient advice, and anomaly detection.

#### Scenario: Harvest prediction
- **WHEN** a user requests harvest prediction
- **THEN** the system analyzes grow timeline and sensor trends to estimate harvest date and expected yield
