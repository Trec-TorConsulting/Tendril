# Capability: Grow Assistant Core (Tendril)

## Purpose
The core platform for the Tendril multi-tenant grow management SaaS. Provides AI-powered conversation, knowledge extraction, context-enriched plant care recommendations, and full grow lifecycle management.

### Tech Stack
- **Backend**: FastAPI (Python 3.12, Uvicorn, async SQLAlchemy)
- **Database**: PostgreSQL (async via asyncpg, Alembic migrations, tenant_id RLS)
- **LLM Chat**: Ollama (llama3.1:8b on node05 GPU)
- **Vision AI**: Google Gemini 2.5-flash (health evaluations)
- **Real-time**: WebSocket streaming with keepalive pings
- **Frontend**: Next.js 16 (Turbopack) + TypeScript + shadcn/ui + Tailwind CSS
- **Storage**: MinIO (S3-compatible, photos/media)
- **MQTT**: EMQX broker, per-tenant topic namespacing
- **Deployment**: K3S namespace `tendril`, 4 deployments (API, MQTT Worker, Scheduler, Web)

## Requirements

### Requirement: Persistent Conversation History
The system SHALL store all conversations and messages in PostgreSQL so that chat history survives pod restarts and redeployments.

#### Scenario: Conversation persists across restarts
- **WHEN** the application pod is restarted
- **THEN** all previous conversations and messages are available in the UI

#### Scenario: CRUD operations on conversations
- **WHEN** a user creates, reads, updates, or deletes a conversation via the API
- **THEN** the operation is persisted and reflected in the UI immediately


### Requirement: Full CRUD on All API Resources
The system SHALL expose Create, Read (single + list), Update, and Delete operations for every persistent API resource unless the resource is a derived view or append-only audit log (see project.md API Design Conventions).

#### Scenario: New resource entity added
- **WHEN** a new persistent entity is introduced (e.g., a new table or data model)
- **THEN** the corresponding store methods (create, get, list, update, delete) and API endpoints (POST, GET, PUT, DELETE) MUST all be implemented before the feature is considered complete

#### Scenario: Audit-log entities
- **WHEN** a resource is an append-only audit trail (e.g., pump dose log, daily scores)
- **THEN** create + read (single and list) operations are sufficient; update and delete MAY be omitted

#### Scenario: Derived/computed views
- **WHEN** a resource is a read-only aggregation (e.g., grow diary, grow score)
- **THEN** only read operations are required


### Requirement: Knowledge Management
The system SHALL store extracted knowledge facts and support listing and deleting them via the API.

#### Scenario: Knowledge CRUD
- **WHEN** a user views or deletes knowledge facts via the API
- **THEN** the knowledge base is updated and future context reflects the change


### Requirement: Grow Cycle Management
The system SHALL support full CRUD on grow cycles including create, read (single + list), update (name, dates, notes), delete, and archive (snapshot buckets and mark completed).

#### Scenario: Create grow cycle
- **WHEN** a user creates a grow cycle via `POST /api/grows`
- **THEN** the cycle is persisted with tent_id, name, start_date, and status=active

#### Scenario: Update grow cycle
- **WHEN** a user updates a grow cycle's name, notes, or dates via `PUT /api/grows/{id}`
- **THEN** the changes are persisted

#### Scenario: Delete grow cycle
- **WHEN** a user deletes a grow cycle via `DELETE /api/grows/{id}`
- **THEN** the cycle is removed from the database

#### Scenario: Archive grow cycle
- **WHEN** a user archives a grow cycle via `POST /api/grows/{id}/archive`
- **THEN** all bucket data is snapshotted into metadata, status is set to completed, and end_date is recorded


### Requirement: AI Chat with Context Enrichment
The system SHALL enrich every chat message with contextual data (latest sensor readings, tent configuration, tent equipment, bucket layout, knowledge facts, and active alerts) before forwarding to the LLM.

#### Scenario: Context-aware response
- **WHEN** a user sends a chat message
- **THEN** the system injects current sensor data, bucket states, tent equipment (type/brand/model/specs), tent size, and knowledge facts into the LLM prompt

#### Scenario: Image analysis
- **WHEN** a user sends a message with a camera snapshot attached
- **THEN** the LLM (LLaVA vision model) analyzes the image alongside the text prompt

### Requirement: AI Accuracy & Honesty
ALL AI systems (Ollama chat, Gemini health checks, coach tips, insights) SHALL enforce strict accuracy and honesty guardrails in every prompt.

#### Scenario: Uncertain answer
- **WHEN** the AI is not confident in an answer
- **THEN** it responds with "I don't know" or "I'm not sure" rather than guessing

#### Scenario: Missing data
- **WHEN** sensor data is missing or stale
- **THEN** the AI explicitly states what data is unavailable rather than assuming values

#### Scenario: Factual claims
- **WHEN** the AI cites sensor readings or measurements
- **THEN** it uses the exact values from the provided context data, not approximations

#### Scenario: Opinion vs fact
- **WHEN** the AI provides advice based on opinion rather than established science
- **THEN** it clearly labels the recommendation as an opinion

#### Scenario: Equipment-aware advice
- **WHEN** tent equipment data (lights, fans, filters, controllers) is available
- **THEN** the AI references specific equipment by brand/model in its recommendations


### Requirement: WebSocket Streaming
The system SHALL stream LLM responses via WebSocket with keepalive pings to prevent connection drops.

#### Scenario: Streaming response
- **WHEN** a user sends a message via the WebSocket endpoint `/ws/chat`
- **THEN** tokens are streamed incrementally as the LLM generates them

#### Scenario: Connection keepalive
- **WHEN** a WebSocket connection is idle during LLM processing
- **THEN** the server sends periodic keepalive pings to prevent timeout


### Requirement: Knowledge Extraction
The system SHALL automatically extract reusable facts from conversations (after 4+ messages) and store them as knowledge events for future context enrichment.

#### Scenario: Auto-summarize conversation
- **WHEN** a conversation reaches 4+ messages and is summarized (manually or automatically)
- **THEN** extracted facts are stored in the events table with type `knowledge`
- **AND** these facts are included in future conversation context

#### Scenario: Knowledge management
- **WHEN** a user views or deletes knowledge facts via the API
- **THEN** the knowledge base is updated and future context reflects the change


### Requirement: Multi-Backend LLM Routing
The system SHALL support routing chat requests to either a local Ollama instance or a RunPod serverless endpoint, with automatic fallback.

#### Scenario: Ollama available
- **WHEN** Ollama is reachable and the configured model is available
- **THEN** chat requests are routed to Ollama

#### Scenario: Ollama unavailable
- **WHEN** Ollama is unreachable or returns an error
- **THEN** the system falls back to RunPod serverless if configured


### Requirement: System Status Endpoint
The system SHALL expose a `/api/status` endpoint reporting connectivity to Ollama, cameras, MQTT, and database.

#### Scenario: Status check
- **WHEN** `GET /api/status` is called
- **THEN** the response includes connectivity status for each subsystem
