# Capability: Camera & Health Checks

## Purpose
Camera snapshot integration and AI-powered plant health evaluations using vision models.

### Camera Sources
- **Primary**: go2rtc frame API (proxied RTSP streams)
- **Fallback**: Direct Reolink HTTP snapshot API
- **No Frigate dependency**: Snapshots fetched independently

### Vision AI
- **Health Checks**: Google Gemini 2.5-flash for detailed markdown health reports
- **Chat Analysis**: LLaVA (via Ollama) for conversational image analysis

## Requirements

### Requirement: Camera Snapshot Retrieval
The system SHALL fetch live JPEG snapshots from configured cameras via go2rtc with Reolink HTTP fallback.

#### Scenario: Snapshot via go2rtc
- **WHEN** `GET /api/snapshot/{tent_id}` is called and go2rtc is reachable
- **THEN** a JPEG frame is returned from the configured go2rtc stream

#### Scenario: Fallback to Reolink
- **WHEN** go2rtc is unreachable
- **THEN** the system falls back to the Reolink camera's direct HTTP snapshot endpoint

#### Scenario: Camera listing
- **WHEN** `GET /api/cameras` is called
- **THEN** all configured tents with their camera stream names are returned


### Requirement: AI Health Evaluations
The system SHALL perform visual plant health assessments by sending camera snapshots with full grow context to a vision AI model and storing the resulting markdown report. Health evaluations support create (trigger), read (single + history), and delete operations.

#### Scenario: Trigger health check
- **WHEN** a user clicks "Health Check" or `POST /api/health-check/{tent_id}` is called
- **THEN** the system captures a snapshot, builds a context prompt (bucket layout, milestones, latest sensors, tent config, tent equipment with brand/model/specs), sends it to Gemini, and stores the markdown report
- **AND** the AI must only report issues confirmed by data, label potential concerns separately, and use exact sensor values from context

#### Scenario: View health history
- **WHEN** `GET /api/health-check/{tent_id}/history` is called
- **THEN** previous health evaluation reports are returned in reverse chronological order

#### Scenario: Delete health evaluation
- **WHEN** `DELETE /api/data/health-evals/{eval_id}` is called
- **THEN** the evaluation report is removed from the database


### Requirement: Dashboard Health Display
The system SHALL display a summary health status badge on the main dashboard page, showing the most recent health score for the user's active grows.

#### Scenario: Health badge on dashboard
- **WHEN** the user views the main dashboard and at least one health check exists
- **THEN** a color-coded health badge is displayed between the camera grid and environment stats showing the score out of 100 with a status label (Healthy / Needs Attention / Critical)

#### Scenario: No health data available
- **WHEN** the user views the main dashboard and no health checks have been run
- **THEN** the health badge section is not rendered


### Requirement: Automated Daily Health Checks
The system SHALL run scheduled daily health evaluations for each configured tent and store the reports in the grow journal.

#### Scenario: Scheduled evaluation
- **WHEN** the scheduler fires at the configured daily time
- **THEN** a health check is performed for each tent and the report is stored as a daily_report event


### Requirement: Snapshot Storage for Comparison
The system SHALL store health check camera snapshots as grow photos in S3/MinIO storage for future comparison and timelapse generation.

#### Scenario: Health check snapshot saved to S3
- **WHEN** a health check is performed (manual or scheduled)
- **THEN** the JPEG snapshot is uploaded to MinIO as a `GrowPhoto` with `source="health_check"` and caption including the health score

#### Scenario: Snapshots appear in grow photos
- **WHEN** a user views the Photos tab for a grow cycle
- **THEN** health check snapshots are listed with a "Health Check" badge alongside user-uploaded photos


### Requirement: Grow Photo Management
The system SHALL support uploading, listing, serving, and deleting grow-level photos stored in S3/MinIO.

#### Scenario: Upload photo
- **WHEN** a user uploads an image via `POST /v1/grows/{id}/photos/grow` (multipart form, JPEG/PNG/WebP, max 10MB)
- **THEN** the file is stored in MinIO at `{tenant_id}/{grow_id}/{uuid}.{ext}` and a `GrowPhoto` record is created

#### Scenario: List grow photos
- **WHEN** `GET /v1/grows/{id}/photos/grow` is called
- **THEN** all photos for that grow cycle are returned, ordered by creation date

#### Scenario: Serve photo from S3
- **WHEN** `GET /v1/grows/{id}/photos/grow/file/{photo_id}` is called with a valid JWT token
- **THEN** the file bytes are streamed from MinIO with the correct content-type

#### Scenario: Delete photo
- **WHEN** `DELETE /v1/grows/{id}/photos/grow/{photo_id}` is called
- **THEN** the file is removed from MinIO and the database record is deleted


### Requirement: Timelapse Generation
The system SHALL generate an animated GIF timelapse from health check snapshots for a grow cycle.

#### Scenario: Generate timelapse
- **WHEN** `GET /v1/grows/{id}/photos/grow/timelapse/{grow_cycle_id}` is called and 2+ health check photos exist
- **THEN** the system fetches all health_check photos from S3, resizes to 640px wide, adds timestamp overlays, and returns an animated GIF (800ms/frame)
