ARG BASE_REGISTRY=registry.registry.svc.cluster.local:5000/mirror
FROM ${BASE_REGISTRY}/python:3.14-slim-bookworm

WORKDIR /app

# Build deps for binary wheels on ARM64
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Reduce image size
RUN find /usr/local -type f -name '*.py[cod]' -delete && \
    find /usr/local -type d -name '__pycache__' -delete

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
