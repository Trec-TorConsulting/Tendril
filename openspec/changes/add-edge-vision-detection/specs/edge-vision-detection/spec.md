## ADDED Requirements

### Requirement: Vision Detection Service
The system SHALL provide a stateless `vision-detector` microservice that loads the active
cannabis detection model and returns object detections for a supplied image. The service
MUST NOT hold tenant database credentials; all persistence is owned by the API.

#### Scenario: Detect objects in an image
- **WHEN** the API sends `POST /detect` to the vision-detector with a JPEG/PNG image and a
  requested detection profile
- **THEN** the service returns a list of detections, each with a class label, confidence
  score (0.0–1.0), and a normalized bounding box `[x, y, w, h]`, plus the accelerator tier
  that served the request and the model version used

#### Scenario: Service exposes health and readiness
- **WHEN** `GET /healthz` is called on the vision-detector
- **THEN** it reports service liveness, the loaded model version (or "none"), and the
  active accelerator tier

#### Scenario: No active model loaded
- **WHEN** a detection is requested and no active model version is available
- **THEN** the service responds with a "detection unavailable" status and the API surfaces
  a graceful "detection not configured" result without erroring the calling feature

### Requirement: Tiered Accelerator Fallback
The system SHALL run detection on the Coral Edge TPU (`node06`) when available and fall
back to a GPU tier (`node05`) and then CPU, recording which tier served each detection.

#### Scenario: Primary Coral TPU path
- **WHEN** the `vision-detector` pod is scheduled on `node06` and the Edge TPU delegate
  loads successfully
- **THEN** detections run on the Coral TPU and each result records `accelerator_tier="coral"`

#### Scenario: Fallback to GPU
- **WHEN** the Edge TPU delegate cannot be initialized or the pod cannot schedule on
  `node06`
- **THEN** the service loads the non-quantized model variant on the GPU tier and records
  `accelerator_tier="gpu"`

#### Scenario: Fallback to CPU
- **WHEN** neither the Coral TPU nor a GPU is available
- **THEN** the service runs on CPU, records `accelerator_tier="cpu"`, and continues to
  return valid detections (degraded latency)

### Requirement: Cannabis Detection Classes
The detection model SHALL support the six v1 target categories: pest/disease spots,
plant/canopy detection, bud/flower detection, nutrient-deficiency leaf regions,
growth-stage classification, and trichome close-up state (clear/cloudy/amber).

#### Scenario: Class taxonomy exposed
- **WHEN** the API queries the active model's metadata
- **THEN** the class list, per-class default confidence thresholds, and expected input
  resolution are returned and used to interpret detections

#### Scenario: Detection profile selects relevant classes
- **WHEN** a scan is requested with a profile (e.g. "tent overview" vs "trichome macro")
- **THEN** only the classes relevant to that profile are evaluated and returned

### Requirement: On-Demand Detection
The system SHALL let a user trigger detection ("Scan") on a live camera snapshot or a
stored/uploaded photo and return persisted detections.

#### Scenario: Scan a tent snapshot
- **WHEN** a user triggers `POST /v1/vision/scan/tent/{tent_id}`
- **THEN** the API captures a snapshot (reusing the camera snapshot pipeline), sends it to
  the vision-detector, persists the detections tenant-scoped, and returns them with
  bounding boxes

#### Scenario: Scan a stored photo
- **WHEN** a user triggers `POST /v1/vision/scan/photo/{photo_id}` for a grow/bucket photo
- **THEN** the API fetches the image from MinIO, runs detection, and persists the results
  linked to that photo and grow cycle

#### Scenario: Detection unavailable degrades gracefully
- **WHEN** a scan is requested but the vision-detector is unreachable or has no active
  model
- **THEN** the API returns a clear "detection unavailable" response without failing the
  page or corrupting grow data

### Requirement: Scheduled Detection
The system SHALL support scheduled detection runs per tent, mirroring the existing daily
health-check scheduler, storing results for review.

#### Scenario: Scheduled tent scan
- **WHEN** the scheduler fires at the configured time for a tent with scheduled scanning
  enabled
- **THEN** a snapshot is captured, detection runs, results are persisted, and any
  actionable findings generate draft records for grower review

#### Scenario: Scheduled scan respects accelerator availability
- **WHEN** a scheduled scan runs while the Coral TPU is unavailable
- **THEN** the scan completes on the GPU or CPU tier and records the tier used

### Requirement: Continuous RTSP Scanning (Feature-Flagged)
The system SHALL implement a continuous RTSP frame-sampling detection mode that is
DISABLED by default and toggleable per tenant/tent for testing.

#### Scenario: Continuous mode disabled by default
- **WHEN** a tenant has not explicitly enabled continuous scanning
- **THEN** no continuous frame sampling occurs and only on-demand and scheduled detection
  are active

#### Scenario: Enable continuous scanning for testing
- **WHEN** a tenant enables the continuous-scan feature flag for a specific tent
- **THEN** the system samples frames at a bounded rate (not full FPS) and runs detection,
  without saturating the single Coral TPU

#### Scenario: Continuous mode is rate-limited
- **WHEN** continuous scanning is active for one or more tents
- **THEN** the frame-sampling rate is capped so the Coral TPU and GPU tiers are not
  overloaded, and overflow is dropped rather than queued unbounded

### Requirement: Detection Persistence and Tenant Isolation
The system SHALL persist detections in a tenant-scoped table protected by PostgreSQL
Row-Level Security, including class, confidence, bounding box, source image reference,
model version, and accelerator tier.

#### Scenario: Detections are tenant-isolated
- **WHEN** a user queries detections
- **THEN** only detections belonging to the caller's tenant are returned, enforced by RLS

#### Scenario: Detection record fields
- **WHEN** a detection is persisted
- **THEN** it stores `tenant_id`, `grow_cycle_id`, `source` (manual/scheduled/continuous),
  source image key, `class`, `confidence`, normalized `bbox`, `model_version`,
  `accelerator_tier`, and `created_at`

### Requirement: Draft Record Generation
The system SHALL convert actionable detections into DRAFT `PestScoutEntry` or `HealthEval`
records for grower review and MUST NOT auto-apply them to grow state.

#### Scenario: Pest/disease detection creates a draft scout entry
- **WHEN** a pest or disease class is detected above its confidence threshold
- **THEN** a draft `PestScoutEntry` is created (tenant-scoped) with the detected species,
  a quality-first severity mapping, grid location when known, and the source photo — marked
  as draft/unconfirmed

#### Scenario: Deficiency detection augments a health eval
- **WHEN** a nutrient-deficiency region is detected
- **THEN** the localized crop is attached to a draft `HealthEval` so the existing
  LLaVA/Gemini pipeline can reason about the "why", without overwriting confirmed evals

#### Scenario: Drafts require human confirmation
- **WHEN** a draft record is generated from a detection
- **THEN** it remains unconfirmed until a user explicitly accepts, edits, or dismisses it

### Requirement: Approval-Gated Actions
The system SHALL route any actionable detection through the existing agentic action
approval lifecycle and MUST NOT execute any mutating action without human approval.

#### Scenario: Actionable finding proposes an approval-gated action
- **WHEN** a detection warrants an action (e.g. treatment task, alert)
- **THEN** the system creates a proposed action via the `grow-assistant-core` action
  lifecycle that requires human approval before execution

#### Scenario: No auto-mutation
- **WHEN** any detection is produced
- **THEN** no grow state, device control, or integration action is executed automatically
  without passing an approval gate

### Requirement: Bounding-Box Overlays
The system SHALL render detection bounding boxes over the corresponding camera feed or
photo in the web UI.

#### Scenario: Overlay on scanned snapshot
- **WHEN** a user views a scanned tent snapshot or photo with detections
- **THEN** color-coded bounding boxes with class labels and confidence are drawn over the
  image, and can be toggled on/off

#### Scenario: Empty detection state
- **WHEN** a scan returns no detections above threshold
- **THEN** the UI shows a clear "no issues detected" state rather than an empty error

### Requirement: Model Artifact Registry
The system SHALL maintain a versioned model registry in MinIO/S3 with an active-version
pointer that the vision-detector loads at startup and can refresh.

#### Scenario: Register a model version
- **WHEN** a new model version is published (by the training change)
- **THEN** a `vision_model_registry` row records the version, storage keys for the Edge-TPU
  and GPU/CPU artifacts, class map, input size, and evaluation metrics

#### Scenario: Activate a model version
- **WHEN** an operator marks a model version active
- **THEN** the vision-detector loads that version and subsequent detections record its
  `model_version`

#### Scenario: Reject incompatible artifact
- **WHEN** the service attempts to load a model whose input size or class map is
  incompatible with the runtime
- **THEN** the load is refused, the previous working model remains active, and the failure
  is logged and surfaced in metrics

### Requirement: Detection Observability
The system SHALL emit metrics for inference latency, accelerator tier used, fallback rate,
and per-class detection counts through the existing monitoring stack.

#### Scenario: Latency and tier metrics
- **WHEN** detections are served
- **THEN** per-request latency and the serving accelerator tier are recorded as metrics

#### Scenario: Fallback rate visibility
- **WHEN** detections fall back from Coral to GPU or CPU
- **THEN** a fallback-rate metric increases so operators can detect Coral/`node06`
  degradation

### Requirement: Secure Self-Hostable Deployment
The vision-detector SHALL be deployable via Kubernetes manifests pinned to `node06`, run
with least privilege, and remain optional so the platform stays self-hostable without a TPU.

#### Scenario: Pinned, least-privilege pod
- **WHEN** the vision-detector is deployed
- **THEN** its pod is scheduled to `node06` via nodeSelector/affinity, runs as non-root
  with a read-only root filesystem and dropped capabilities, and exposes only an
  internal ClusterIP service

#### Scenario: Optional deployment
- **WHEN** an operator self-hosts Tendril without a Coral TPU and without deploying the
  vision-detector
- **THEN** all existing features continue to work and detection features report as
  unavailable rather than failing
