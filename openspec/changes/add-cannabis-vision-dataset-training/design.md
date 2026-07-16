## Context
The inference change (`add-edge-vision-detection`) needs a cannabis-tuned YOLOv5-class
model published to the `vision_model_registry`. Producing that model requires a labeled
dataset, a GPU training run, Edge-TPU compilation, and quality gates. Tendril is a public
AGPL/MIT project, so dataset licensing and attribution are first-class constraints. A GPU
exists on `node05`; MinIO/S3 is available for staging. The grower already stores labeled
grow imagery in S3.

## Goals / Non-Goals
- Goals:
  - Produce reproducible, licensed, quality-gated model artifacts consumable by the
    inference service.
  - Supplement the grower's own images with permissively licensed public data.
  - Keep external/staged data ephemeral to conserve storage.
  - Bias evaluation toward cannabis-quality-protective recall.
- Non-Goals:
  - Serving inference (owned by `add-edge-vision-detection`).
  - Continuous online/active learning (future work).
  - Redistributing third-party datasets — we consume under-license and attribute.

## Decisions

- **Decision: Offline training Job on `node05`, not a request-path service.**
  Training is batch, GPU-heavy, and infrequent. It runs as a Kubernetes Job (or local dev
  invocation) and writes artifacts to MinIO + the registry.
  - Alternatives considered: in-cluster always-on trainer (wasteful — rejected).

- **Decision: Strict license allowlist + per-source attribution manifest, enforced before training.**
  Only CC0 / CC-BY / public-domain / explicitly redistribution-or-training-permitting
  licensed sources are ingested. Each source records name, URL, license, and attribution.
  The pipeline refuses to train if any staged source lacks a verified permissive license.
  - Alternatives considered: "any public image" (user rejected — legal risk for a public
    repo).

- **Decision: Ephemeral staging for external data; grower photos are read-only and never deleted.**
  Supplemental images are downloaded into an isolated MinIO prefix/bucket used only for a
  training run, then deleted on completion (success or failure). The grower's own S3 photos
  are referenced read-only.
  - Alternatives considered: persist curated dataset long-term (user chose ephemeral).

- **Decision: YOLOv5-class + Ultralytics; dual export (Edge-TPU int8 tflite + ONNX/torch).**
  Matches the inference service's Coral-first, GPU/CPU-fallback design. Int8 quantization
  uses a representative calibration subset; a non-quantized variant serves GPU/CPU tiers.
  - Alternatives considered: newest YOLO (worse Coral op coverage — rejected).

- **Decision: Cannabis-quality-weighted acceptance gates.**
  Publishing requires minimum overall mAP AND minimum **recall** on quality-threatening
  classes (mold/botrytis, spider mites, powdery mildew). A model that misses these fails
  the gate even if overall mAP is acceptable — protecting resin/terpene/cannabinoid
  quality first.

- **Decision: Full provenance recorded per model version.**
  Each published version stores its dataset manifest, source attributions, class map,
  training config, hyperparameters, and random seeds for reproducibility and auditability.

## Risks / Trade-offs
- **Domain gap of general leaf-disease corpora** → Weight cannabis-native sources higher;
  use general corpora only for augmentation; validate on cannabis-only held-out set.
- **Class imbalance (rare pests/diseases)** → Targeted supplementation, augmentation, and
  per-class thresholds; recall-weighted gates catch under-detection.
- **License misclassification** → Manual verification step + machine-readable license field
  required per source; hard fail if missing/unknown.
- **Quantization accuracy drop** → Compare int8 vs fp metrics; gate on the int8 (Edge-TPU)
  metrics since that is the primary serving tier.
- **Storage bloat from staging** → Enforced post-run cleanup; staging isolated from durable
  buckets.

## Migration Plan
- Additive, offline. First run publishes the initial active model, which flips detection
  from "unavailable" to active in `add-edge-vision-detection`.
- Rollback: deactivate/replace the model version in the registry; delete the artifact.
  No effect on other subsystems.

## Open Questions
- Exact mAP/recall thresholds per class — set empirically from the first labeled dataset.
- Whether to keep a small, fully-owned/licensed "golden" validation set persistent (not
  ephemeral) for regression comparison across model versions.
