ARG BASE_REGISTRY=registry.registry.svc.cluster.local:5000/mirror

FROM ${BASE_REGISTRY}/python:3.14-slim-bookworm AS runtime
WORKDIR /app

RUN useradd --create-home --uid 1000 tendril

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/local -type f -name '*.py[cod]' -delete && \
    find /usr/local -type d -name '__pycache__' -delete

COPY app ./app
RUN chown -R tendril:tendril /app
USER tendril

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request as u,sys; sys.exit(0 if u.urlopen('http://localhost:8080/healthz',timeout=2).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
