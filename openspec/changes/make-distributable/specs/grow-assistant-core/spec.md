## ADDED Requirements

### Requirement: Configurable LLM Backend
The system SHALL support pluggable LLM backends configured at startup or via the setup wizard. Supported backends: Ollama (native API) and any OpenAI-compatible API endpoint.

#### Scenario: Ollama backend configured
- **WHEN** the LLM backend is set to `ollama` with a base URL
- **THEN** chat requests are routed to the Ollama API

#### Scenario: OpenAI-compatible backend configured
- **WHEN** the LLM backend is set to `openai` with a base URL and optional API key
- **THEN** chat requests are routed using the OpenAI chat completions API format

#### Scenario: No LLM configured
- **WHEN** no LLM backend is configured
- **THEN** the chat feature is disabled and the UI shows a setup prompt

---

### Requirement: First-Run Setup Wizard
The system SHALL display a guided setup wizard on first launch (no config or no users) that walks the user through configuring admin account, tents, cameras, LLM, vision AI, and MQTT.

#### Scenario: First launch
- **WHEN** the app starts with no existing configuration or users
- **THEN** the setup wizard is displayed instead of the main app

#### Scenario: Wizard completion
- **WHEN** the user completes all wizard steps
- **THEN** the configuration is saved and the app redirects to the main view

#### Scenario: Re-run wizard
- **WHEN** an admin clicks "Re-run Setup" in settings
- **THEN** the setup wizard opens pre-populated with current configuration

---

### Requirement: Unified Configuration System
The system SHALL load configuration from environment variables, `config.yaml`, and database settings (in that priority order), with sensible defaults for all optional values.

#### Scenario: Environment variable override
- **WHEN** an environment variable is set (e.g., `OLLAMA_URL`)
- **THEN** it overrides the corresponding value in `config.yaml` and database

#### Scenario: Zero-config startup
- **WHEN** the app starts with no config file and no environment variables
- **THEN** the app starts with SQLite, no cameras, no LLM, and displays the setup wizard

## MODIFIED Requirements

### Requirement: Multi-Backend LLM Routing
The system SHALL support routing chat requests to a configured LLM backend (Ollama or OpenAI-compatible) based on the unified configuration system, with graceful degradation when the backend is unavailable.

#### Scenario: Configured backend available
- **WHEN** the configured LLM backend is reachable
- **THEN** chat requests are routed to it

#### Scenario: Backend unavailable
- **WHEN** the configured LLM backend is unreachable
- **THEN** the system returns a user-friendly error and the chat shows a connection warning

### Requirement: System Status Endpoint
The system SHALL expose a `/api/status` endpoint reporting connectivity to all configured subsystems (LLM, cameras, MQTT, database) based on the active configuration. Unconfigured subsystems are reported as `disabled`.

#### Scenario: Status check with partial config
- **WHEN** `GET /api/status` is called and MQTT is not configured
- **THEN** the MQTT status is reported as `disabled` (not `error`)
