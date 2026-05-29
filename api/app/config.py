from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


def _require_env(name: str) -> str:
    """Return an env var or raise with a clear message."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"{name} environment variable is required")
    return val


@dataclass(frozen=True)
class Settings:
    # Database — required, no default
    database_url: str = field(default_factory=lambda: _require_env("DATABASE_URL"))
    database_pool_size: int = field(default_factory=lambda: int(os.environ.get("DATABASE_POOL_SIZE", "10")))

    # Redis (optional — middleware falls back to in-memory without it)
    redis_url: str = field(default_factory=lambda: os.environ.get("REDIS_URL", ""))

    # Auth
    jwt_secret: str = field(default_factory=lambda: os.environ["JWT_SECRET"])
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # OAuth2 providers
    google_client_id: str = field(default_factory=lambda: os.environ.get("GOOGLE_CLIENT_ID", ""))
    google_client_secret: str = field(default_factory=lambda: os.environ.get("GOOGLE_CLIENT_SECRET", ""))
    github_client_id: str = field(default_factory=lambda: os.environ.get("GITHUB_CLIENT_ID", ""))
    github_client_secret: str = field(default_factory=lambda: os.environ.get("GITHUB_CLIENT_SECRET", ""))

    # MQTT / EMQX
    mqtt_broker_host: str = field(
        default_factory=lambda: os.environ.get("MQTT_BROKER_HOST", "emqx.emqx.svc.cluster.local")
    )
    mqtt_broker_port: int = field(default_factory=lambda: int(os.environ.get("MQTT_BROKER_PORT", "8883")))

    # Ollama
    ollama_base_url: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_BASE_URL", "http://ollama.ollama.svc.cluster.local:11434")
    )
    ollama_model: str = field(default_factory=lambda: os.environ.get("OLLAMA_MODEL", "mistral-nemo:12b"))
    ollama_vision_model: str = field(default_factory=lambda: os.environ.get("OLLAMA_VISION_MODEL", "llava:13b"))

    # Gemini (used for health checks)
    gemini_api_key: str = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"))

    # Stripe
    stripe_secret_key: str = field(default_factory=lambda: os.environ.get("STRIPE_SECRET_KEY", ""))
    stripe_webhook_secret: str = field(default_factory=lambda: os.environ.get("STRIPE_WEBHOOK_SECRET", ""))

    # Integrations
    integration_encryption_key: str = field(default_factory=lambda: os.environ.get("INTEGRATION_ENCRYPTION_KEY", ""))

    # S3 / MinIO
    s3_endpoint: str = field(
        default_factory=lambda: os.environ.get("S3_ENDPOINT", "http://minio.minio.svc.cluster.local:9000")
    )
    s3_access_key: str = field(default_factory=lambda: os.environ.get("S3_ACCESS_KEY", "minioadmin"))
    s3_secret_key: str = field(default_factory=lambda: os.environ.get("S3_SECRET_KEY", ""))
    s3_bucket: str = field(default_factory=lambda: os.environ.get("S3_BUCKET", "tendril-photos"))

    # Web Push (VAPID)
    vapid_private_key: str = field(default_factory=lambda: os.environ.get("VAPID_PRIVATE_KEY", ""))
    vapid_email: str = field(default_factory=lambda: os.environ.get("VAPID_EMAIL", "mailto:admin@tendrilgrow.com"))

    # Email (Resend)
    resend_api_key: str = field(default_factory=lambda: os.environ.get("RESEND_API_KEY", ""))
    email_from: str = field(default_factory=lambda: os.environ.get("EMAIL_FROM", "Tendril <noreply@tendrilgrow.com>"))

    # Stripe Tax
    stripe_tax_enabled: bool = field(
        default_factory=lambda: os.environ.get("STRIPE_TAX_ENABLED", "true").lower() == "true"
    )

    # Dunning
    dunning_grace_days: int = field(default_factory=lambda: int(os.environ.get("DUNNING_GRACE_DAYS", "14")))

    # Account deletion
    data_retention_days: int = field(default_factory=lambda: int(os.environ.get("DATA_RETENTION_DAYS", "30")))

    # App
    app_name: str = "Tendril"
    domain: str = field(default_factory=lambda: os.environ.get("DOMAIN", "tendrilgrow.com"))
    api_prefix: str = "/v1"
    cors_origins: list[str] = field(
        default_factory=lambda: os.environ.get("CORS_ORIGINS", "https://tendrilgrow.com").split(",")
    )
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
