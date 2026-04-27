# Change: Make Distributable (Open-Source Distro)

## Why
The Grow Assistant is currently hardcoded for one specific setup (Reolink cameras, EMQX MQTT, PostgreSQL, specific Ollama models, Gemini API, K3S deployment). To release as an open-source project that anyone can run on their home network, we need configurable providers, a Docker Compose deployment, SQLite as the default database, a first-run setup wizard, and removal of all hardcoded assumptions.

## What Changes
- Add Docker Compose deployment (no K8s required)
- Add first-run setup wizard UI for cameras, LLM, vision AI, MQTT, and database
- Add pluggable camera backends: RTSP generic, USB webcam, ONVIF discovery, Reolink, Wyze, Amcrest, TP-Link
- Add pluggable LLM backends: Ollama + any OpenAI-compatible API (LM Studio, vLLM, text-generation-webui)
- Add pluggable vision AI: Gemini, OpenAI Vision, LLaVA (local via Ollama)
- Add SQLite as default database (PostgreSQL optional)
- Make MQTT optional (app works without sensors)
- Make ESP32 sensor hardware optional
- Add environment-based configuration (`config.yaml` or `.env`)
- Add example `.env` and `docker-compose.yml`
- Create `README.md` with quick-start guide for home users
- **BREAKING**: Configuration format changes (env vars become structured config)

## Impact
- Affected specs: ALL (every capability becomes configurable)
- Affected code: `app/main.py`, `app/store.py` (dual DB support, now includes `yields` table, `analyze_bucket_drift()`, `get_bucket_sensor_history_since()`), `app/camera_client.py` (pluggable), `app/ollama_client.py` (pluggable), `app/gemini_client.py` (pluggable), `app/mqtt_client.py` (optional), `app/scheduler.py` (includes drift check loop), new `app/config.py`, new `docker-compose.yml`
- **BREAKING**: Configuration format and deployment model changes
