## Context
The Grow Assistant is built for a specific K3S cluster with hardcoded Reolink cameras, EMQX MQTT, PostgreSQL, and Ollama. To release as an open-source distro, every integration point needs to be configurable and the deployment model must be simple enough for home users with no Kubernetes experience.

## Goals / Non-Goals
- **Goals**: One-command deployment via Docker Compose, guided setup wizard, pluggable providers for cameras/LLM/vision/DB/MQTT, works on any Linux/macOS/Windows machine with Docker
- **Non-Goals**: Kubernetes Helm chart (keep existing K8s manifests but don't make them the primary path), mobile native apps, multi-user SaaS, cloud hosting

## Decisions

### Default Database
- **Decision**: SQLite by default, PostgreSQL as optional upgrade
- **Rationale**: Zero setup for home users. SQLite handles single-user writes fine. PG available for power users or multi-instance deployments.
- **Alternative**: PostgreSQL only (bundled in compose) — rejected because it adds memory overhead and complexity for Raspberry Pi users

### Camera Plugin Architecture
- **Decision**: Python ABC with `get_snapshot(stream_id) -> bytes` interface, loaded by config
- **Rationale**: Simple, no plugin registry needed, each backend is a Python module. Camera type specified in config per tent.
- **Backends**: go2rtc (proxy), Reolink HTTP, generic RTSP (via ffmpeg subprocess), USB webcam (OpenCV), ONVIF, Wyze (docker-wyze-bridge API)
- **Alternative**: Camera abstraction via go2rtc only — rejected because not all users run go2rtc

### LLM Plugin Architecture
- **Decision**: Abstract interface with `chat(messages, model) -> str` and `stream(messages, model) -> AsyncGenerator`
- **Backends**: Ollama (native API), OpenAI-compatible (covers LM Studio, vLLM, LocalAI, text-generation-webui)
- **Rationale**: OpenAI-compatible API is the de facto standard. Two backends cover 95% of local LLM setups.

### Configuration Hierarchy
- **Decision**: Environment variables override `config.yaml` which overrides defaults
- **Rationale**: Env vars for Docker/K8s, config file for manual management, sensible defaults for zero-config start
- **Storage**: User-modified settings (from setup wizard/UI) stored in database, merged at runtime

### Container Architecture
- **Decision**: Single container with multi-arch (AMD64 + ARM64) image
- **Rationale**: Simplicity for home users. One `docker run` or `docker-compose up`. ARM64 for Raspberry Pi users.
- **Alternative**: Separate containers for frontend/backend/worker — rejected (overengineered for single-user)

## Risks / Trade-offs
- **SQLite concurrent writes**: Single-writer limitation. Mitigated by WAL mode and the fact that home use is single-user.
- **ffmpeg dependency for RTSP**: Need ffmpeg in the Docker image. Adds ~80MB to image size. Acceptable.
- **USB webcam in Docker**: Requires `--device=/dev/video0` mount. May confuse some users. Document clearly.
- **Wyze integration**: Depends on docker-wyze-bridge running separately. Document as optional.

## Migration Plan
1. Refactor current code to use abstraction layers (no user-facing changes)
2. Add config system with backward-compatible env var support
3. Add SQLite backend alongside PostgreSQL
4. Create Docker Compose file
5. Add setup wizard
6. Publish Docker image to Docker Hub / GitHub Container Registry
7. Existing K8s manifests continue to work (not removed)

## Open Questions
- Should we publish to Docker Hub under a project name (e.g., `growassistant/grow-assistant`)?
- Should the setup wizard support importing config from another instance (backup/restore)?
- Should we support Tailscale/WireGuard for remote access out of the box?
