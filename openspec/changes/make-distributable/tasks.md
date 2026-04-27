## 1. Configuration System
- [ ] 1.1 Create `app/config.py` — unified config loader (env vars → config.yaml → defaults)
- [ ] 1.2 Define config schema: database, llm, vision, cameras, mqtt, general settings
- [ ] 1.3 Create `config.example.yaml` with all options documented
- [ ] 1.4 Create `.env.example` with environment variable mappings
- [ ] 1.5 Add `GET /api/config` endpoint (returns non-sensitive config for frontend)
- [ ] 1.6 Add `PUT /api/config` endpoint (admin-only, updates config at runtime)
- [ ] 1.7 Store user-modified config in database (survives container restarts)

## 2. Database Abstraction
- [ ] 2.1 Create `app/db.py` — database abstraction layer (interface for SQLite + PostgreSQL)
- [ ] 2.2 Implement SQLite backend with same schema as PostgreSQL
- [ ] 2.3 Auto-detect database type from config (`DATABASE_URL` or `sqlite:///data/grow.db`)
- [ ] 2.4 Handle SQLite-specific differences (no RETURNING, different timestamp handling)
- [ ] 2.5 Default to SQLite with data stored in `/data/grow.db` (volume-mounted)
- [ ] 2.6 Add database migration system (versioned schema with upgrade path)
- [ ] 2.7 Migrate `app/store.py` to use the abstraction layer

## 3. Pluggable Camera Backends
- [ ] 3.1 Create `app/cameras/base.py` — abstract camera interface (get_snapshot, list_streams)
- [ ] 3.2 Implement `app/cameras/rtsp.py` — generic RTSP snapshot via ffmpeg
- [ ] 3.3 Implement `app/cameras/reolink.py` — current Reolink HTTP client (refactored)
- [ ] 3.4 Implement `app/cameras/go2rtc.py` — current go2rtc client (refactored)
- [ ] 3.5 Implement `app/cameras/usb.py` — USB webcam via OpenCV/v4l2
- [ ] 3.6 Implement `app/cameras/onvif.py` — ONVIF device discovery and snapshot
- [ ] 3.7 Implement `app/cameras/wyze.py` — Wyze camera bridge integration
- [ ] 3.8 Add camera auto-detection in setup wizard (scan for ONVIF, RTSP, Reolink on LAN)
- [ ] 3.9 Update `/api/cameras` and `/api/snapshot/{tent_id}` to use pluggable backend

## 4. Pluggable LLM Backends
- [ ] 4.1 Create `app/llm/base.py` — abstract LLM interface (chat, stream, list_models)
- [ ] 4.2 Implement `app/llm/ollama.py` — current Ollama client (refactored)
- [ ] 4.3 Implement `app/llm/openai_compat.py` — OpenAI-compatible API (works with LM Studio, vLLM, text-generation-webui, LocalAI)
- [ ] 4.4 Update chat routing to use configured LLM backend
- [ ] 4.5 Add model selection in settings UI
- [ ] 4.6 Add LLM connection test in setup wizard

## 5. Pluggable Vision AI Backends
- [ ] 5.1 Create `app/vision/base.py` — abstract vision interface (analyze_image)
- [ ] 5.2 Implement `app/vision/gemini.py` — current Gemini client (refactored)
- [ ] 5.3 Implement `app/vision/openai_vision.py` — OpenAI Vision API (GPT-4o, etc.)
- [ ] 5.4 Implement `app/vision/local_llava.py` — LLaVA via Ollama (no cloud key needed)
- [ ] 5.5 Update health check to use configured vision backend
- [ ] 5.6 Add API key input in setup wizard (for Gemini/OpenAI)

## 6. Optional MQTT
- [ ] 6.1 Make MQTT connection conditional — skip if no MQTT config provided
- [ ] 6.2 App fully functional without MQTT (manual sensor entry only)
- [ ] 6.3 Add MQTT section in setup wizard (optional)
- [ ] 6.4 Support user-provided MQTT broker (any broker, not just EMQX)

## 7. Docker Compose Deployment
- [ ] 7.1 Create `docker-compose.yml` with grow-assistant service
- [ ] 7.2 Include optional PostgreSQL service (commented out, use if not using SQLite)
- [ ] 7.3 Include optional Mosquitto service (commented out, use if needed)
- [ ] 7.4 Volume mounts for `/data` (SQLite DB, config), `/static` (custom assets)
- [ ] 7.5 Multi-arch Docker image (AMD64 + ARM64) via GitHub Actions or buildx
- [ ] 7.6 Create `Dockerfile` optimized for both architectures
- [ ] 7.7 Health check in compose file
- [ ] 7.8 Create `.env.example` with all configuration options

## 8. First-Run Setup Wizard
- [ ] 8.1 Detect first-run state (no config file or no users in DB)
- [ ] 8.2 Create setup wizard UI — multi-step form:
  - Step 1: Welcome + create admin account
  - Step 2: Configure tents (name, count)
  - Step 3: Configure cameras (type, URL/IP per tent — with test button)
  - Step 4: Configure LLM (Ollama URL or OpenAI-compatible endpoint — with test button)
  - Step 5: Configure Vision AI (Gemini key, OpenAI key, or local LLaVA — with test button)
  - Step 6: Optional MQTT broker
  - Step 7: Review & finish
- [ ] 8.3 Save wizard results to config.yaml + database
- [ ] 8.4 Redirect to main app after wizard completion
- [ ] 8.5 Allow re-running wizard from settings (admin only)

## 9. Documentation
- [ ] 9.1 Create distro README.md with quick-start guide
- [ ] 9.2 Document all configuration options
- [ ] 9.3 Document supported camera types with setup instructions
- [ ] 9.4 Document supported LLM backends with setup instructions
- [ ] 9.5 Add troubleshooting section
- [ ] 9.6 Add architecture diagram for the distro

## 10. Testing
- [ ] 10.1 Test SQLite backend (CRUD for all entities)
- [ ] 10.2 Test PostgreSQL backend (same tests)
- [ ] 10.3 Test each camera backend with mock
- [ ] 10.4 Test LLM backend switching
- [ ] 10.5 Test app startup without MQTT
- [ ] 10.6 Test Docker Compose deployment on fresh machine
- [ ] 10.7 Test setup wizard end-to-end
- [ ] 10.8 Test multi-arch image build
