# Change: Add Edge Vision Detection (Coral TPU Cannabis Object Detection)

## Why
Tendril already captures camera snapshots and runs vision *reasoning* via LLaVA/Gemini
(see `openspec/specs/camera-health-checks/spec.md`), but it has no fast, deterministic
*object detection* — the ability to localize and count pests, disease spots, buds,
deficiency regions, plants, and trichomes with bounding boxes. A Google Coral Edge TPU
is available on cluster node `node06`, giving us cheap, low-power (~2W), millisecond-scale
inference that can run continuously across every tent camera without burdening the
GPU/LLM stack.

Detection is **complementary** to the existing LLM vision, not a replacement: YOLO
localizes and counts, then the existing LLaVA/Gemini pipeline can reason about the
relevant crops. This directly serves the cannabis-first quality philosophy in
`openspec/project.md` — earlier, more objective detection of quality-threatening issues
(mold, mites, powdery mildew, deficiencies) means faster protection of resin, terpenes,
and cannabinoid maturity.

This change covers the **inference service and application integration only**. Producing
the model (dataset curation, training, Edge-TPU export) is a separate change:
`add-cannabis-vision-dataset-training`.

## What Changes
- Add a new **`vision-detector` service** (self-hostable microservice) that loads a
  cannabis-tuned YOLOv5-class model and exposes a detection API over HTTP.
- Add a **tiered accelerator fallback**: Coral Edge TPU on `node06` → GPU (Ollama node
  `node05`) → CPU, so detection still works — degraded but functional — if the TPU or a
  node is unavailable. Preserves the "must remain self-hostable" constraint.
- Support the initial **six detection targets** (classes) selected for v1: pest/disease
  spots, plant/canopy detection & counting, bud/flower detection & counting,
  nutrient-deficiency leaf localization, growth-stage classification, and trichome
  close-up state (clear/cloudy/amber).
- Add **on-demand detection** ("Scan" a tent snapshot or an uploaded/stored photo) and
  **scheduled detection** (mirroring the existing daily health-check scheduler).
- Add a **continuous RTSP scanning** mode that is **implemented but disabled by default**,
  toggleable per tenant/tent via a feature flag for testing.
- **Persist detections** (class, confidence, bounding box, source image) tenant-scoped
  via RLS, and generate **draft** `PestScoutEntry` / `HealthEval` records for grower
  review — never auto-applied.
- Route any **actionable** finding through the existing agentic **action approval
  lifecycle** (`grow-assistant-core`) with a human gate; nothing auto-acts.
- Add **bounding-box overlay** rendering so detections display on the camera feed and
  photo views.
- Add a **model artifact registry** in MinIO/S3 (versioned models + metadata) with an
  "active version" pointer the service loads at startup / on refresh.
- Add **observability** (inference latency, accelerator tier used, fallback rate,
  per-class detection counts) via the existing metrics stack.

## Impact
- Affected specs:
  - edge-vision-detection (NEW capability)
  - camera-health-checks (MODIFIED — add scan triggers + detection overlays on snapshots)
- Affected code (expected):
  - NEW `vision-detector/` service (Python; ultralytics/onnxruntime + pycoral) with its
    own Dockerfile
  - NEW `manifests/vision-detector-deployment.yaml`, `-service.yaml` (nodeSelector to
    `node06`, Coral device access, non-root, read-only rootfs)
  - `api/app/` new `vision/` domain: async client, scan routes, detection models, draft
    generators, scheduler hook
  - `api/app/ai/` — reuse action approval lifecycle for actionable detections
  - `web/src/` — Scan button, detection overlay component, detections list UI
- Data model impact (new tables approved):
  - `vision_detections` (tenant_id, grow_cycle_id, source, image key, class, confidence,
    bbox, model_version, accelerator_tier, created_at)
  - `vision_model_registry` (version, storage key, classes, metrics, active flag)
  - draft linkage into existing `pest_scout_entries` / `health_evals`
- Security impact:
  - tenant isolation via RLS on all detection/draft rows
  - `vision-detector` runs non-root, read-only rootfs, no tenant DB access (stateless
    inference only; API owns persistence)
  - Coral device exposure scoped to the single pinned pod; SSRF-safe internal-only
    service address
- Breaking changes:
  - none; entirely additive and feature-flagged. Detection is optional and degrades
    gracefully when no camera, no model, or no accelerator is present.
