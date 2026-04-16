from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    # Database
    database_url: str = field(
        default_factory=lambda: os.environ.get(
            "DATABASE_URL",
            "postgresql+asyncpg://tendril:tendril@postgresql.postgresql.svc.cluster.local:5432/tendril",
        )
    )
    database_pool_size: int = field(
        default_factory=lambda: int(os.environ.get("DATABASE_POOL_SIZE", "10"))
    )

    # Auth
    jwt_secret: str = field(
        default_factory=lambda: os.environ["JWT_SECRET"]
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # OAuth2 providers
    google_client_id: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CLIENT_ID", "")
    )
    google_client_secret: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_CLIENT_SECRET", "")
    )
    github_client_id: str = field(
        default_factory=lambda: os.environ.get("GITHUB_CLIENT_ID", "")
    )
    github_client_secret: str = field(
        default_factory=lambda: os.environ.get("GITHUB_CLIENT_SECRET", "")
    )

    # MQTT / EMQX
    mqtt_broker_host: str = field(
        default_factory=lambda: os.environ.get(
            "MQTT_BROKER_HOST", "emqx.emqx.svc.cluster.local"
        )
    )
    mqtt_broker_port: int = field(
        default_factory=lambda: int(os.environ.get("MQTT_BROKER_PORT", "8883"))
    )

    # Ollama
    ollama_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "OLLAMA_BASE_URL", "http://ollama.ollama.svc.cluster.local:11434"
        )
    )
    ollama_model: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_MODEL", "llama3.2")
    )

    # Stripe
    stripe_secret_key: str = field(
        default_factory=lambda: os.environ.get("STRIPE_SECRET_KEY", "")
    )
    stripe_webhook_secret: str = field(
        default_factory=lambda: os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    )

    # Web Push (VAPID)
    vapid_private_key: str = field(
        default_factory=lambda: os.environ.get("VAPID_PRIVATE_KEY", "")
    )
    vapid_email: str = field(
        default_factory=lambda: os.environ.get("VAPID_EMAIL", "mailto:admin@tendril.maddscientist.com")
    )

    # App
    app_name: str = "Tendril"
    domain: str = field(
        default_factory=lambda: os.environ.get("DOMAIN", "tendril.maddscientist.com")
    )
    api_prefix: str = "/v1"
    cors_origins: list[str] = field(
        default_factory=lambda: os.environ.get(
            "CORS_ORIGINS", "https://tendril.maddscientist.com"
        ).split(",")
    )
    log_level: str = field(
        default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO")
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
