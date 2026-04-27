## ADDED Requirements

### Requirement: Pluggable Camera Backends
The system SHALL support configurable camera backends per tent. Supported types: go2rtc proxy, Reolink HTTP, generic RTSP, USB webcam, ONVIF, Wyze, Amcrest, TP-Link.

#### Scenario: RTSP camera configured
- **WHEN** a tent's camera is configured with type `rtsp` and a stream URL
- **THEN** snapshots are captured via ffmpeg from the RTSP stream

#### Scenario: USB webcam configured
- **WHEN** a tent's camera is configured with type `usb` and a device path
- **THEN** snapshots are captured via the local video device

#### Scenario: No camera configured
- **WHEN** no camera is configured for a tent
- **THEN** the snapshot button is hidden and health checks that require vision are disabled

---

### Requirement: Pluggable Vision AI Backends
The system SHALL support configurable vision AI backends for health evaluations. Supported: Google Gemini, OpenAI Vision (GPT-4o), local LLaVA via Ollama.

#### Scenario: Gemini configured
- **WHEN** the vision backend is set to `gemini` with a valid API key
- **THEN** health checks use the Gemini API for image analysis

#### Scenario: Local LLaVA configured
- **WHEN** the vision backend is set to `local_llava` with an Ollama URL
- **THEN** health checks use LLaVA via Ollama (no cloud API key required)

#### Scenario: OpenAI Vision configured
- **WHEN** the vision backend is set to `openai` with a valid API key
- **THEN** health checks use the OpenAI Vision API

## MODIFIED Requirements

### Requirement: Camera Snapshot Retrieval
The system SHALL fetch live JPEG snapshots from configured cameras using the pluggable camera backend system. Each tent's camera type and connection details are defined in the configuration.

#### Scenario: Snapshot via configured backend
- **WHEN** `GET /api/snapshot/{tent_id}` is called
- **THEN** a JPEG frame is returned from the tent's configured camera backend

#### Scenario: Camera unreachable
- **WHEN** the configured camera is unreachable
- **THEN** the system returns an error response and the UI shows a camera offline indicator

### Requirement: AI Health Evaluations
The system SHALL perform visual plant health assessments using the configured vision AI backend. The prompt includes full grow context (bucket layout, milestones, latest sensors, tent config).

#### Scenario: Trigger health check
- **WHEN** a user clicks "Health Check" or `POST /api/health-check/{tent_id}` is called
- **THEN** the system captures a snapshot via the configured camera backend, sends it with context to the configured vision AI backend, and stores the markdown report
