## ADDED Requirements

### Requirement: Licensed Dataset Sourcing
The system SHALL only ingest supplemental images under open/permissive licenses
(CC0, CC-BY, public domain, or licenses explicitly permitting model-training use) and MUST
record a per-source attribution manifest.

#### Scenario: Permissive source accepted
- **WHEN** a supplemental dataset with a verified CC0/CC-BY/public-domain license is added
- **THEN** its images are staged for training and the source name, URL, license, and
  attribution are recorded in the dataset manifest

#### Scenario: Non-permissive or unknown-license source rejected
- **WHEN** a source has an unknown, restrictive, or missing license
- **THEN** the pipeline refuses to stage it and fails the run with a clear licensing error

#### Scenario: Outbound source URLs are validated
- **WHEN** the pipeline fetches images from an external URL
- **THEN** the URL is validated against an allowlist to prevent SSRF and only expected
  hosts are contacted

### Requirement: Ephemeral Staging and Cleanup
The system SHALL stage external/supplemental images in an isolated MinIO location used only
for a training run and SHALL delete that staged data after the run completes, while never
deleting the grower's own photos.

#### Scenario: Staged data deleted after successful training
- **WHEN** a training run completes successfully
- **THEN** the ephemeral staged external images are deleted and the storage is reclaimed

#### Scenario: Staged data deleted after failed training
- **WHEN** a training run fails or is aborted
- **THEN** the ephemeral staged external images are still cleaned up

#### Scenario: Grower photos are read-only
- **WHEN** the pipeline references the grower's existing S3 grow/bucket/health-check photos
- **THEN** those images are read only and are never modified or deleted by the pipeline

### Requirement: Detection Class Taxonomy
The dataset labels SHALL be normalized to the six v1 detection classes so trained models
are compatible with the inference service: pest/disease, plant/canopy, bud/flower,
nutrient-deficiency region, growth-stage, and trichome state.

#### Scenario: Labels normalized to taxonomy
- **WHEN** images from multiple sources with differing label names are curated
- **THEN** their labels are mapped to the canonical class taxonomy, and unmapped labels are
  flagged for review rather than silently dropped

#### Scenario: Taxonomy matches the inference model metadata
- **WHEN** a model is published
- **THEN** its class map exactly matches the taxonomy expected by the inference service

### Requirement: Reproducible Training Pipeline
The system SHALL train a YOLOv5-class model using Ultralytics tooling on the GPU node with
reproducible configuration and seeds.

#### Scenario: Train on GPU node
- **WHEN** a training run is started
- **THEN** it executes on the GPU node (`node05`) using the curated dataset and a recorded
  training configuration

#### Scenario: Reproducible run
- **WHEN** a model version is produced
- **THEN** the training config, hyperparameters, and random seeds are recorded with the
  version so the run can be reproduced

### Requirement: Edge-TPU and Fallback Export
The system SHALL export each trained model as an int8, Edge-TPU-compiled artifact for the
Coral tier and a non-quantized ONNX/torch artifact for the GPU/CPU tiers.

#### Scenario: Edge-TPU compilation
- **WHEN** a trained model passes evaluation
- **THEN** it is int8-quantized using a representative calibration subset and compiled with
  the Edge TPU compiler into a `_edgetpu.tflite` artifact

#### Scenario: Fallback variant produced
- **WHEN** the model is exported
- **THEN** a non-quantized ONNX/torch variant is also produced for the GPU and CPU
  inference tiers

### Requirement: Quality-Weighted Acceptance Gates
The system SHALL require minimum overall mAP AND minimum recall on quality-threatening
classes before a model may be published, prioritizing cannabis quality protection.

#### Scenario: Model passes gates
- **WHEN** a trained model meets the overall mAP threshold and the recall thresholds for
  mold/botrytis, spider mites, and powdery mildew on the held-out cannabis validation set
- **THEN** the model is eligible for publishing

#### Scenario: Model fails quality recall gate
- **WHEN** a model meets overall mAP but misses the recall threshold on a
  quality-threatening class
- **THEN** the model is rejected and not published, even though overall mAP is acceptable

#### Scenario: Gate uses Edge-TPU metrics
- **WHEN** evaluating for the acceptance gate
- **THEN** the int8/Edge-TPU variant's metrics are used, since that is the primary serving
  tier

### Requirement: Model Publishing and Provenance
The system SHALL publish passing models to the `vision_model_registry` with full provenance,
including dataset manifest, source attributions, class map, input size, and metrics.

#### Scenario: Publish to registry
- **WHEN** a model passes the acceptance gates
- **THEN** its Edge-TPU and fallback artifacts are uploaded to MinIO and a
  `vision_model_registry` entry is created with version, storage keys, class map, input
  size, and evaluation metrics

#### Scenario: Provenance recorded
- **WHEN** a model version is published
- **THEN** its dataset manifest and per-source attributions are stored alongside the model
  artifacts for audit and licensing compliance

#### Scenario: First published model activates detection
- **WHEN** the first passing model version is published and marked active
- **THEN** the inference service can load it and detection becomes available platform-wide
