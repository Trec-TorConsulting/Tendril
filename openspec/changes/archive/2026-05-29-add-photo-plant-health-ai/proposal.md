# Change: Add Photo-Based Plant Health AI

## Why
Plantix has answered 100M+ crop questions using camera-based AI diagnosis. No cannabis-specific equivalent exists. Growers (especially beginners) struggle to identify nutrient deficiencies, pest infestations, and diseases. Tendril already runs Ollama on a Jetson node — adding vision model support (LLaVA, BakLLaVA, or Gemini Vision) enables point-and-diagnose from the PWA camera. This is the #1 missing AI feature identified in competitive analysis.

## What Changes

### New: Photo Diagnosis Endpoint
- `POST /v1/ai/diagnose` — Upload a photo of a plant, receive AI diagnosis
- Accepts image (JPEG/PNG), grow context (grow_type, current_stage, recent_readings)
- Returns: identified issue(s), confidence score, treatment recommendations, severity level
- Uses vision-capable model (LLaVA on Ollama for local, Gemini Vision for cloud fallback)
- Responses are grow-type-aware (e.g., "In DWC, yellow leaves with brown spots usually indicates pH lockout" vs generic)

### New: Plant Health Photo Log
- `POST /v1/grows/{id}/health-photos` — Log a diagnosed photo with results
- `GET /v1/grows/{id}/health-photos` — View diagnosis history with photos
- Stored in MinIO (images) + PostgreSQL (metadata + AI results)
- Timeline view shows plant health progression over time

### New: Treatment Recommendations Database
- Structured database of cannabis-specific issues: deficiencies (N, P, K, Ca, Mg, Fe, Mn, Zn, S, B, Cu, Mo), pests (spider mites, fungus gnats, thrips, aphids, whiteflies, root aphids), diseases (powdery mildew, botrytis, root rot, fusarium, pythium)
- Each entry: symptoms, photo examples, causes, treatments by grow type, prevention
- AI diagnosis links to database entries for structured treatment plans

### New: PWA Camera Integration
- Camera capture button on grow detail page
- Real-time camera preview with "Diagnose" button
- Results overlay on photo with issue regions highlighted (if model supports)
- Save to health photo log or dismiss

## Impact
- Affected code: `api/app/ai/` (new vision routes), `api/app/grows/` (health photo routes), frontend (camera component), MinIO (photo storage)
- New spec: `ai-plant-health`
- Depends on: Ollama with vision model, or Gemini Vision API key
