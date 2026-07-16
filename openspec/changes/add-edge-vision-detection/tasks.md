# Implementation Tasks — Add Edge Vision Detection

## 1. Vision-Detector Service (new microservice)
- [x] 1.1 Scaffold `vision-detector/` service (Python) with `POST /detect`, `GET /healthz`
- [ ] 1.2 Implement model loader that reads the active model version from the registry
- [ ] 1.3 Implement Coral Edge TPU inference path (`pycoral`/`libedgetpu`, int8 tflite)
- [ ] 1.4 Implement GPU inference path (ONNX/torch, non-quantized variant)
- [ ] 1.5 Implement CPU inference path and the tiered fallback selection logic
- [ ] 1.6 Return detections with class, confidence, normalized bbox, model version, tier
- [x] 1.7 Add graceful "no active model" and "unavailable" responses
- [x] 1.8 Write `vision-detector/Dockerfile` (arm64, non-root, read-only rootfs friendly)
- [x] 1.9 Unit tests for fallback selection, response schema, and no-model handling

## 2. Kubernetes Deployment
- [x] 2.1 `manifests/vision-detector-deployment.yaml` pinned to `node06` (nodeSelector/affinity)
- [x] 2.2 Expose the Coral device to the pod; least-privilege securityContext
- [x] 2.3 `manifests/vision-detector-service.yaml` (internal ClusterIP only)
- [x] 2.4 GPU-tier scheduling config referencing `node05` for fallback
- [x] 2.5 NetworkPolicy: only the API may reach the vision-detector
- [x] 2.6 Liveness/readiness probes wired to `/healthz`

## 3. API — Vision Domain
- [ ] 3.1 Add `vision_detections` and `vision_model_registry` models + Alembic migration
- [ ] 3.2 Enable RLS policies on the new tenant-scoped tables
- [x] 3.3 Async client for the vision-detector with timeouts and graceful degradation
- [x] 3.4 `POST /v1/vision/scan/tent/{tent_id}` (reuse snapshot pipeline)
- [x] 3.5 `POST /v1/vision/scan/photo/{photo_id}` (fetch from MinIO)
- [ ] 3.6 `GET /v1/vision/detections` (tenant-scoped, paginated)
- [ ] 3.7 Model registry endpoints: list versions, activate version
- [x] 3.8 Permission guards (`require_permission()`) on all new routes
- [x] 3.9 Input validation (Pydantic) and OpenAPI docs

## 4. Detection → Drafts → Approval
- [ ] 4.1 Map detected classes to quality-first severity + draft `PestScoutEntry`
- [ ] 4.2 Attach deficiency crops to draft `HealthEval` for LLaVA/Gemini reasoning
- [ ] 4.3 Route actionable findings through the `grow-assistant-core` action lifecycle
- [ ] 4.4 Ensure no auto-mutation without an approval gate (tests asserting this)

## 5. Scheduled + Continuous Modes
- [ ] 5.1 Add scheduled tent-scan job to the existing scheduler
- [ ] 5.2 Implement continuous RTSP frame sampler, DISABLED by default
- [ ] 5.3 Per-tenant/per-tent feature flag to toggle continuous mode
- [ ] 5.4 Bounded-rate sampling with overflow drop (no unbounded queue)

## 6. Web UI
- [ ] 6.1 "Scan" button on tent camera and photo views
- [ ] 6.2 Bounding-box overlay component (toggle, color-coded, labels + confidence)
- [ ] 6.3 Detections list + draft review (accept/edit/dismiss) UI
- [ ] 6.4 Empty-state and "detection unavailable" states
- [ ] 6.5 Vitest component tests + Playwright e2e for scan + overlay

## 7. Observability
- [ ] 7.1 Metrics: inference latency, accelerator tier, fallback rate, per-class counts
- [ ] 7.2 ServiceMonitor / dashboard panel for detection health
- [ ] 7.3 Structured logs for model load, fallback events, and load rejections

## 8. Validation & Docs
- [ ] 8.1 `openspec validate add-edge-vision-detection --strict --no-interactive`
- [ ] 8.2 Add docs page (detection overview, self-hosting without a TPU, feature flags)
- [ ] 8.3 Zero-regression check: all existing API/web tests pass
- [ ] 8.4 Security review: RLS, least-privilege pod, internal-only service, no auto-act
