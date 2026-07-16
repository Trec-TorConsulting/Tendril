# Implementation Tasks — Add Cannabis Vision Dataset & Training Pipeline

## 1. Dataset Sourcing & Licensing
- [ ] 1.1 Define the license allowlist (CC0 / CC-BY / public domain / training-permitted)
- [ ] 1.2 Build a per-source attribution manifest schema (name, URL, license, attribution)
- [ ] 1.3 Curate candidate permissive sources (Roboflow Universe cannabis sets, Kaggle
      "Leaf Manifestation Diseases of Cannabis", iNaturalist/GBIF CC imagery) — verify each license
- [ ] 1.4 Implement SSRF-safe fetcher with an outbound host allowlist
- [ ] 1.5 Hard-fail the run on any unknown/missing/restrictive license

## 2. Ephemeral Staging & Hygiene
- [ ] 2.1 Provision an isolated MinIO bucket/prefix for per-run staging
- [ ] 2.2 Reference grower S3 photos read-only (no writes/deletes)
- [ ] 2.3 Implement post-run cleanup (delete staged external data on success AND failure)
- [ ] 2.4 Verify storage reclamation with a size assertion after cleanup

## 3. Curation & Labeling
- [ ] 3.1 Define canonical class taxonomy matching the six inference classes
- [ ] 3.2 Label-normalization mapping across heterogeneous source label names
- [ ] 3.3 Flag unmapped labels for review (no silent drops)
- [ ] 3.4 Merge grower imagery + supplemental data into a unified YOLO dataset layout
- [ ] 3.5 Build held-out cannabis-only validation split (optionally a persistent golden set)

## 4. Training Pipeline
- [ ] 4.1 Scaffold `vision-training/` offline pipeline (Ultralytics YOLOv5-class)
- [ ] 4.2 Reproducible config + fixed seeds; record hyperparameters
- [ ] 4.3 `manifests/vision-training-job.yaml` targeting GPU `node05`, ephemeral staging
- [ ] 4.4 Train run produces weights + training logs/metrics

## 5. Export & Compilation
- [ ] 5.1 Int8 quantization with a representative calibration subset
- [ ] 5.2 Edge TPU compilation → `_edgetpu.tflite`
- [ ] 5.3 Non-quantized ONNX/torch export for GPU/CPU tiers
- [ ] 5.4 Validate artifact input size + class map compatibility with the inference runtime

## 6. Evaluation & Gates
- [ ] 6.1 Compute overall mAP and per-class recall on the held-out set (int8 metrics)
- [ ] 6.2 Enforce quality-weighted gates (recall on mold/mites/powdery mildew)
- [ ] 6.3 Reject models failing the quality recall gate regardless of overall mAP
- [ ] 6.4 Emit an evaluation report artifact

## 7. Publishing & Provenance
- [ ] 7.1 Upload Edge-TPU + fallback artifacts to MinIO under a versioned prefix
- [ ] 7.2 Create `vision_model_registry` entry (version, keys, class map, input size, metrics)
- [ ] 7.3 Store dataset manifest + attributions alongside the model
- [ ] 7.4 Support marking a version active (first passing model activates detection)

## 8. Validation & Docs
- [ ] 8.1 `openspec validate add-cannabis-vision-dataset-training --strict --no-interactive`
- [ ] 8.2 Docs: dataset sourcing/licensing policy, training run guide, cleanup behavior
- [ ] 8.3 Legal/licensing review of the attribution manifest and allowlist
- [ ] 8.4 Reproducibility check: re-run from recorded config/seeds yields equivalent metrics
