## Context
Tendril has cameras (go2rtc/RTSP + Reolink HTTP snapshots), MinIO/S3 photo storage, an
LLM vision pipeline (LLaVA/Gemini), and an agentic action approval lifecycle. It does not
have deterministic object detection. A Google Coral Edge TPU is physically attached to
k3s node `node06`; a GPU used by Ollama is on `node05`. The platform must remain
self-hostable, multi-tenant (RLS), OWASP-compliant, and cannabis-quality-first.

## Goals / Non-Goals
- Goals:
  - Fast, cheap, deterministic detection + localization of cannabis-relevant objects.
  - Run primarily on the Coral TPU, but degrade gracefully to GPU then CPU.
  - Integrate detections into existing pest-scout/health-eval data and the approval-gated
    action lifecycle — never auto-act.
  - Keep the inference service stateless and secure; the API owns all persistence.
- Non-Goals:
  - Training the model, dataset curation, or Edge-TPU compilation (separate change
    `add-cannabis-vision-dataset-training`).
  - Replacing the LLaVA/Gemini reasoning pipeline.
  - Real-time multi-camera high-FPS video analytics (continuous mode ships disabled).

## Decisions

- **Decision: Separate stateless `vision-detector` microservice, not in-process in the API.**
  The Coral runtime (`pycoral`/`libedgetpu`) needs device access and a pinned node; the
  API is horizontally autoscaled (HPA) and must stay portable. A dedicated service pinned
  to `node06` isolates hardware concerns. The API calls it over an internal-only HTTP
  endpoint.
  - Alternatives considered: API sidecar (couples HPA pods to the TPU node — rejected);
    in-process TFLite in the API (blocks event loop, can't use the TPU from many pods —
    rejected).

- **Decision: Three-tier accelerator fallback — Coral (`node06`) → GPU (`node05`) → CPU.**
  The service detects available accelerators at startup and per request-routing. If the
  Edge TPU delegate fails to load or the pod can't schedule on `node06`, it falls back to
  a GPU-backed ONNX/torch runtime on `node05`, then to CPU. Every detection records which
  tier served it.
  - Alternatives considered: Coral-only (user rejected — no resilience); always-CPU
    (defeats the purpose).

- **Decision: YOLOv5-class, int8, Edge-TPU-compiled model as the primary artifact; a
  non-quantized (fp16/fp32) ONNX/torch variant for the GPU/CPU tiers.**
  Modern YOLOv8/v11 ops partially fall back to CPU on the Edge TPU, negating its benefit;
  YOLOv5-class exports cleanly via the edgetpu compiler. The registry stores both the
  `_edgetpu.tflite` and the `.onnx`/`.pt` variants for one logical model version.
  - Alternatives considered: newest YOLO everywhere (worse Coral utilization — user
    rejected).

- **Decision: Detections are advisory. Draft records + approval gates only.**
  Every detection persists as a `vision_detections` row. When a detection maps to an
  actionable concern, the system creates a **draft** `PestScoutEntry` or `HealthEval` and,
  if it warrants action, routes it through the existing `grow-assistant-core` action
  lifecycle (propose → approve → execute). No auto-mutation of grow state.

- **Decision: Model artifact registry in MinIO/S3 with an active-version pointer.**
  The training change publishes model artifacts + metadata (classes, input size, metrics)
  under a versioned prefix. `vision_model_registry` tracks versions and which is active.
  The service loads the active version at startup and can hot-refresh on signal.

- **Decision: Continuous RTSP scan mode ships fully implemented but disabled by default.**
  A per-tenant/per-tent feature flag enables a bounded-rate frame sampler (not full FPS)
  so the single Coral is not saturated. Default off; intended for testing and opt-in.

## Risks / Trade-offs
- **Single Coral is a throughput bottleneck** → Bounded scan rate; on-demand + scheduled
  are the primary modes; continuous mode is opt-in and rate-limited. GPU tier absorbs
  overflow.
- **`node06` is a single point of failure for the fast tier** → GPU/CPU fallback keeps
  detection functional; detections record degraded tier for observability.
- **False positives could alarm growers** → Confidence thresholds per class; drafts, not
  facts; human approval gate before any action; cannabis-quality-first severity mapping.
- **Model/runtime version drift between service and registry** → Registry stores input
  size + class map with each version; service validates compatibility on load and refuses
  incompatible artifacts.
- **Device security exposure** → Only the pinned pod mounts the Coral device; service is
  stateless, non-root, read-only rootfs, no DB credentials, internal ClusterIP only.

## Migration Plan
- Purely additive; no schema changes to existing tables (new tables only).
- Ship with detection **off** (no active model version → API returns "detection
  unavailable"); enabling requires the training change to publish an active model.
- Rollback: scale `vision-detector` to zero and clear the active model version; the API
  degrades gracefully and all existing features are unaffected.

## Open Questions
- Exact confidence thresholds per class — to be tuned during the training change against
  a held-out validation set and the cannabis-quality severity mapping.
- Whether continuous mode should sample from go2rtc frames or decode RTSP directly in the
  detector — decide during implementation based on `node06` load.
