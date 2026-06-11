## 1. AI Vision Integration
- [x] 1.1 Add vision model to Ollama (LLaVA or BakLLaVA) on Jetson node
- [x] 1.2 Create `POST /v1/ai/diagnose` endpoint — accept image + grow context, return diagnosis
- [x] 1.3 Build prompt engineering for cannabis-specific plant health diagnosis
- [x] 1.4 Add Gemini Vision fallback for cloud-capable deployments
- [x] 1.5 Add grow-type-aware context injection (DWC diagnosis differs from soil diagnosis)

## 2. Treatment Database
- [x] 2.1 Create treatment database schema (issues, symptoms, treatments, prevention)
- [x] 2.2 Populate nutrient deficiency entries (N, P, K, Ca, Mg, Fe, Mn, Zn, S, B, Cu, Mo)
- [x] 2.3 Populate pest entries (spider mites, fungus gnats, thrips, aphids, whiteflies, root aphids)
- [x] 2.4 Populate disease entries (PM, botrytis, root rot, fusarium, pythium)
- [x] 2.5 Link AI diagnosis output to treatment database entries

## 3. Health Photo Log API
- [x] 3.1 Create health_photos table (migration, model, RLS)
- [x] 3.2 Create `POST /v1/grows/{id}/health-photos` — store photo + diagnosis
- [x] 3.3 Create `GET /v1/grows/{id}/health-photos` — list with pagination
- [x] 3.4 MinIO integration for photo storage

## 4. Frontend
- [x] 4.1 PWA camera capture component (MediaDevices API)
- [x] 4.2 Diagnosis result display with treatment links
- [x] 4.3 Health photo timeline view on grow detail page
- [x] 4.4 Treatment database browsable UI

## 5. Testing
- [x] 5.1 API tests for diagnose endpoint
- [x] 5.2 API tests for health photo CRUD
- [x] 5.3 Treatment database completeness test
