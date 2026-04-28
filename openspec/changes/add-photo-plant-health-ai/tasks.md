## 1. AI Vision Integration
- [ ] 1.1 Add vision model to Ollama (LLaVA or BakLLaVA) on Jetson node
- [ ] 1.2 Create `POST /v1/ai/diagnose` endpoint — accept image + grow context, return diagnosis
- [ ] 1.3 Build prompt engineering for cannabis-specific plant health diagnosis
- [ ] 1.4 Add Gemini Vision fallback for cloud-capable deployments
- [ ] 1.5 Add grow-type-aware context injection (DWC diagnosis differs from soil diagnosis)

## 2. Treatment Database
- [ ] 2.1 Create treatment database schema (issues, symptoms, treatments, prevention)
- [ ] 2.2 Populate nutrient deficiency entries (N, P, K, Ca, Mg, Fe, Mn, Zn, S, B, Cu, Mo)
- [ ] 2.3 Populate pest entries (spider mites, fungus gnats, thrips, aphids, whiteflies, root aphids)
- [ ] 2.4 Populate disease entries (PM, botrytis, root rot, fusarium, pythium)
- [ ] 2.5 Link AI diagnosis output to treatment database entries

## 3. Health Photo Log API
- [ ] 3.1 Create health_photos table (migration, model, RLS)
- [ ] 3.2 Create `POST /v1/grows/{id}/health-photos` — store photo + diagnosis
- [ ] 3.3 Create `GET /v1/grows/{id}/health-photos` — list with pagination
- [ ] 3.4 MinIO integration for photo storage

## 4. Frontend
- [ ] 4.1 PWA camera capture component (MediaDevices API)
- [ ] 4.2 Diagnosis result display with treatment links
- [ ] 4.3 Health photo timeline view on grow detail page
- [ ] 4.4 Treatment database browsable UI

## 5. Testing
- [ ] 5.1 API tests for diagnose endpoint
- [ ] 5.2 API tests for health photo CRUD
- [ ] 5.3 Treatment database completeness test
