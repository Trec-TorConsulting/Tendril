ARG BASE_REGISTRY=registry.registry.svc.cluster.local:5000/mirror

# ── Builder: collect/compile wheels with the build toolchain ──────
FROM ${BASE_REGISTRY}/python:3.14-slim-bookworm AS builder
WORKDIR /app
# Build deps for binary wheels (asyncpg, bcrypt, …) on ARM64
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ── Runtime: slim image, no toolchain, runs as non-root ───────────
FROM ${BASE_REGISTRY}/python:3.14-slim-bookworm AS runtime
WORKDIR /app
# Unprivileged user; uid 1000 matches the k8s securityContext runAsUser.
RUN useradd --create-home --uid 1000 tendril
# Install from the prebuilt wheels so gcc/python3-dev never land in the
# final image.
COPY requirements.txt .
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels && \
    find /usr/local -type f -name '*.py[cod]' -delete && \
    find /usr/local -type d -name '__pycache__' -delete

COPY . .
RUN chown -R tendril:tendril /app
USER tendril

EXPOSE 8000

# Container-level liveness for docker/compose runtimes. Kubernetes ignores
# this and uses its own readiness/liveness probes.
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request as u,sys; sys.exit(0 if u.urlopen('http://localhost:8000/health',timeout=2).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
