from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.auth.routes import router as auth_router
from app.tenants.routes import router as tenants_router
from app.devices.routes import router as devices_router
from app.grows.grow_type_routes import router as grow_types_router
from app.grows.tent_routes import router as tents_router
from app.grows.grow_routes import router as grows_router
from app.grows.bucket_routes import router as buckets_router
from app.grows.journal_routes import router as journal_router
from app.grows.photo_routes import router as photos_router
from app.grows.feeding_routes import router as feeding_router
from app.grows.strain_routes import router as strains_router
from app.grows.yield_routes import router as yields_router
from app.sensors.routes import router as sensors_router
from app.weather.routes import router as weather_router
from app.reference.routes import router as reference_router
from app.ai.routes import router as ai_router
from app.automation.routes import router as automation_router
from app.notifications.routes import router as notifications_router
from app.billing.routes import router as billing_router
from app.data.routes import router as data_router
from app.commercial.grow_type_routes import router as custom_grow_types_router
from app.commercial.task_routes import router as tasks_router
from app.commercial.audit_routes import router as audit_router
from app.commercial.api_key_routes import router as api_keys_router
from app.admin.routes import router as admin_router

logger = logging.getLogger("tendril")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
    logger.info("Tendril API starting up")
    yield
    logger.info("Tendril API shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url=f"{settings.api_prefix}/docs",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    # Security middleware
    from app.middleware.security import SecurityHeadersMiddleware
    from app.middleware.rate_limit import RateLimiter
    from app.middleware.brute_force import BruteForceProtection

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimiter)
    app.add_middleware(BruteForceProtection)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
    app.include_router(tenants_router, prefix=f"{settings.api_prefix}/tenants", tags=["tenants"])
    app.include_router(devices_router, prefix=f"{settings.api_prefix}/devices", tags=["devices"])
    app.include_router(grow_types_router, prefix=f"{settings.api_prefix}/grow-types", tags=["grow-types"])
    app.include_router(tents_router, prefix=f"{settings.api_prefix}/tents", tags=["tents"])
    app.include_router(grows_router, prefix=f"{settings.api_prefix}/grows", tags=["grows"])
    app.include_router(buckets_router, prefix=f"{settings.api_prefix}/buckets", tags=["buckets"])
    app.include_router(sensors_router, prefix=f"{settings.api_prefix}/sensors", tags=["sensors"])
    app.include_router(journal_router, prefix=f"{settings.api_prefix}/journal", tags=["journal"])
    app.include_router(photos_router, prefix=f"{settings.api_prefix}/photos", tags=["photos"])
    app.include_router(feeding_router, prefix=f"{settings.api_prefix}/feeding", tags=["feeding"])
    app.include_router(strains_router, prefix=f"{settings.api_prefix}/strains", tags=["strains"])
    app.include_router(yields_router, prefix=f"{settings.api_prefix}/yields", tags=["yields"])
    app.include_router(weather_router, prefix=f"{settings.api_prefix}/weather", tags=["weather"])
    app.include_router(reference_router, prefix=f"{settings.api_prefix}/reference", tags=["reference"])
    app.include_router(ai_router, prefix=f"{settings.api_prefix}/ai", tags=["ai"])
    app.include_router(automation_router, prefix=f"{settings.api_prefix}/automation", tags=["automation"])
    app.include_router(notifications_router, prefix=f"{settings.api_prefix}/notifications", tags=["notifications"])
    app.include_router(billing_router, prefix=f"{settings.api_prefix}/billing", tags=["billing"])
    app.include_router(data_router, prefix=f"{settings.api_prefix}/data", tags=["data"])
    app.include_router(custom_grow_types_router, prefix=f"{settings.api_prefix}/custom-grow-types", tags=["custom-grow-types"])
    app.include_router(tasks_router, prefix=f"{settings.api_prefix}/tasks", tags=["tasks"])
    app.include_router(audit_router, prefix=f"{settings.api_prefix}/audit", tags=["audit"])
    app.include_router(api_keys_router, prefix=f"{settings.api_prefix}/api-keys", tags=["api-keys"])
    app.include_router(admin_router, prefix=f"{settings.api_prefix}/admin", tags=["admin"])

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
