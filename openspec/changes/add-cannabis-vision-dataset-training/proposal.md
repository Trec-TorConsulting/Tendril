# Change: Add Cannabis Vision Dataset & Training Pipeline

## Why
The `add-edge-vision-detection` change adds a Coral-TPU inference service but deliberately
does not produce a model. This change defines how Tendril curates a labeled cannabis image
dataset, trains a YOLOv5-class detector, exports it for the Coral Edge TPU (plus GPU/CPU
variants), evaluates it against cannabis-quality criteria, and publishes versioned artifacts
into the model registry the inference service consumes.

Tendril already accumulates labeled-in-context grow imagery in MinIO/S3 (health-check
snapshots, grow/bucket photos tagged with strain, stage, and issues) — a strong labeling
head start. To reach usable per-class accuracy, the grower's own images are **supplemented
with openly/permissively licensed public datasets**. Because Tendril is a public, AGPL/MIT
open-source project, dataset sourcing MUST respect licensing and attribution, and staged
external data MUST be ephemeral (cleaned up after training) to save storage.

## What Changes
- Add a **dataset sourcing policy**: only openly/permissively licensed images
  (CC0 / CC-BY / public domain, or explicitly redistribution-permitting dataset licenses),
  with a tracked **attribution manifest** per source.
- Add an **ephemeral MinIO staging** area: external/supplemental images are downloaded to a
  dedicated, isolated bucket/prefix for training, then **deleted after training completes**
  to reclaim space. The grower's own photos are never deleted by this process.
- Add a **class taxonomy** aligned exactly with the six v1 detection targets:
  pest/disease, plant/canopy, bud/flower, nutrient-deficiency region, growth-stage,
  trichome state (clear/cloudy/amber).
- Add a **curation & labeling workflow** combining the grower's existing S3 imagery with
  the supplemental sources, normalizing labels to the taxonomy.
- Add a **training pipeline** using Ultralytics YOLOv5-class tooling, running on the GPU
  node (`node05`), with reproducible configs and seeds.
- Add **Edge-TPU export/compilation** (int8 quantization + `edgetpu_compiler`) plus a
  non-quantized ONNX/torch variant for the GPU/CPU inference tiers.
- Add **evaluation & acceptance gates**: minimum per-class mAP thresholds and a
  cannabis-quality bias (recall on quality-threatening classes — mold, mites, powdery
  mildew — weighted highest) before a model may be published.
- Add **artifact publishing** to the `vision_model_registry` (version, storage keys,
  class map, input size, metrics) consumed by `add-edge-vision-detection`.
- Add **provenance & reproducibility**: every published model records its dataset manifest,
  source attributions, training config, and seeds.
- Add **storage hygiene**: automated cleanup of ephemeral staged data and enforcement that
  no unlicensed/attribution-missing source is included.

### Candidate public sources (licenses MUST be verified per dataset before use)
- **Roboflow Universe** cannabis datasets — e.g. disease/pest (caterpillar, mealybug,
  powdery mildew, spider mite, rust), bud/flower, sex/growth-stage & node datasets,
  cannabis leaf counter, and UAV/plant detection sets. Licenses vary per dataset
  (CC BY 4.0 / MIT / Public Domain / others) — filter to permissive only.
- **Kaggle** — "Leaf Manifestation Diseases of Cannabis" and similar leaf-disease sets
  (verify license).
- **General leaf-disease corpora** (e.g. PlantVillage-style) for augmentation of
  deficiency/disease visual features (verify license, note domain gap vs cannabis).
- **iNaturalist / GBIF** cannabis observations for plant/canopy imagery under CC licenses
  (filter to CC0/CC-BY, capture attribution).

## Impact
- Affected specs:
  - cannabis-vision-training (NEW capability)
- Affected code (expected):
  - NEW `vision-training/` pipeline (dataset fetch, license/attribution manifest,
    label normalization, train, export, evaluate, publish) — run as a Job/offline tool,
    not a request-path service
  - NEW `manifests/vision-training-job.yaml` (GPU on `node05`, ephemeral staging PVC/bucket)
  - Writes to `vision_model_registry` (owned by `add-edge-vision-detection`)
- Data model impact:
  - reuses `vision_model_registry`; adds a dataset/provenance manifest artifact per model
    version (stored in MinIO alongside the model)
- Security / legal impact:
  - license allowlist + attribution manifest enforced before training
  - ephemeral external data deleted post-training; no PII; no unlicensed redistribution
  - all outbound source URLs validated/allowlisted (SSRF-safe)
- Breaking changes:
  - none; offline pipeline, additive.
