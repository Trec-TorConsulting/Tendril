ARG BASE_REGISTRY=registry.registry.svc.cluster.local:5000/mirror

FROM ${BASE_REGISTRY}/python:3.14-slim-bookworm AS runtime
WORKDIR /app

RUN useradd --create-home --uid 1000 tendril

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/local -type f -name '*.py[cod]' -delete && \
    find /usr/local -type d -name '__pycache__' -delete

RUN python - <<'PY'
import pathlib
import urllib.request

model_url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.onnx"
out_path = pathlib.Path("/app/models/model.onnx")
out_path.parent.mkdir(parents=True, exist_ok=True)
urllib.request.urlretrieve(model_url, str(out_path))
print(f"Downloaded model to {out_path}")
PY

COPY app ./app
RUN chown -R tendril:tendril /app
USER tendril

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request as u,sys; sys.exit(0 if u.urlopen('http://localhost:8080/healthz',timeout=2).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
