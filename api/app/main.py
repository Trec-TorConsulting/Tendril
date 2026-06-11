from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.admin.routes import router as admin_router
from app.ai.conversation_routes import router as conversation_router
from app.ai.diagnose_routes import router as diagnose_router
from app.ai.routes import router as ai_router
from app.auth.routes import router as auth_router
from app.automation.routes import router as automation_router
from app.billing.account_deletion import router as account_deletion_router
from app.billing.cancellation import router as billing_cancel_router
from app.billing.invoices import router as billing_invoices_router
from app.billing.metrics import router as billing_metrics_router
from app.billing.plans import router as billing_plans_router
from app.billing.provider_admin import router as billing_providers_router
from app.billing.routes import router as billing_router
from app.commercial.api_key_routes import router as api_keys_router
from app.commercial.audit_routes import router as audit_router
from app.commercial.grow_type_routes import router as custom_grow_types_router
from app.commercial.task_routes import router as tasks_router
from app.config import get_settings
from app.config_management.routes import router as config_mgmt_router
from app.data.routes import router as data_router
from app.devices.commands import router as device_commands_router
from app.devices.routes import router as devices_router
from app.equipment.routes import router as equipment_router
from app.grows.bucket_routes import router as buckets_router
from app.grows.expense_routes import router as expense_router
from app.grows.feeding_routes import router as feeding_router
from app.grows.field_canvas_routes import router as field_canvas_router
from app.grows.grow_routes import router as grows_router
from app.grows.grow_type_routes import router as grow_types_router
from app.grows.journal_routes import router as journal_router
from app.grows.photo_routes import router as photos_router
from app.grows.quick_log_routes import router as quick_log_router
from app.grows.strain_routes import router as strains_router
from app.grows.tent_routes import router as tents_router
from app.grows.yield_routes import router as yields_router
from app.integrations.routes import router as integrations_router
from app.logging_config import setup_logging
from app.notifications.internal_routes import router as internal_alerts_router
from app.notifications.routes import router as notifications_router
from app.outdoor.companion_routes import router as companion_router
from app.outdoor.container_routes import router as container_router
from app.outdoor.intelligence_routes import router as intelligence_router
from app.outdoor.pest_routes import router as pest_router
from app.outdoor.plot_routes import router as plot_router
from app.outdoor.runoff_routes import router as runoff_router
from app.outdoor.soil_routes import router as soil_router
from app.outdoor.yield_routes import router as harvest_yield_router
from app.reference.routes import router as reference_router
from app.sensors.routes import router as sensors_router
from app.sensors.tent_routes import router as tent_sensors_router
from app.support.admin_routes import router as support_admin_router
from app.support.forum_routes import router as forum_router
from app.support.kb_routes import router as kb_router
from app.support.routes import router as support_tickets_router
from app.tenants.routes import router as tenants_router
from app.weather.routes import router as weather_router

logger = logging.getLogger("tendril")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Tendril API starting up")

    # Auto-seed reference data
    try:
        from app.data.seed_treatments import seed_treatments
        from app.database import async_session_factory
        from app.reference.nutrient_sync import sync_seed_nutrients
        from app.reference.strain_sync import sync_seed_strains
        from app.support.kb_seed import sync_kb_seed

        async with async_session_factory() as session:
            await sync_seed_strains(session)
            await sync_seed_nutrients(session)
            await seed_treatments(session)
        async with async_session_factory() as session:
            await sync_kb_seed(session)
        logger.info("Reference data seeding complete")
    except Exception as e:
        logger.warning("Reference data seeding failed (non-fatal): %s", e)

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
        redirect_slashes=False,
    )

    # Prometheus metrics
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator(
        excluded_handlers=["/health", "/health/ready", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics")

    # Security middleware
    from app.middleware.brute_force import BruteForceProtection
    from app.middleware.csrf import CSRFMiddleware
    from app.middleware.rate_limit import RateLimiter
    from app.middleware.request_logging import RequestLoggingMiddleware
    from app.middleware.security import SecurityHeadersMiddleware
    from app.middleware.tenant_plan import TenantPlanMiddleware

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TenantPlanMiddleware)
    app.add_middleware(CSRFMiddleware)
    app.add_middleware(RateLimiter)
    app.add_middleware(BruteForceProtection)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-CSRF-Token"],
    )

    # Ensure CORS headers are present on error responses (BaseHTTPMiddleware can
    # interfere with CORSMiddleware's ability to inject headers on exceptions).
    from fastapi import Request
    from fastapi.exceptions import HTTPException as FastAPIHTTPException
    from starlette.exceptions import HTTPException as StarletteHTTPException

    def _cors_headers(request: Request) -> dict[str, str]:
        origin = request.headers.get("origin", "")
        if origin in settings.cors_origins:
            return {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
            }
        return {}

    @app.exception_handler(StarletteHTTPException)
    async def cors_http_exception_handler(request: Request, exc: StarletteHTTPException):
        headers = {**_cors_headers(request), **(exc.headers or {})}
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )

    @app.exception_handler(FastAPIHTTPException)
    async def cors_fastapi_exception_handler(request: Request, exc: FastAPIHTTPException):
        headers = {**_cors_headers(request), **(exc.headers or {})}
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )

    # Routers
    app.include_router(auth_router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
    app.include_router(tenants_router, prefix=f"{settings.api_prefix}/tenants", tags=["tenants"])
    app.include_router(devices_router, prefix=f"{settings.api_prefix}/devices", tags=["devices"])
    app.include_router(device_commands_router, prefix=f"{settings.api_prefix}/devices", tags=["device-commands"])
    app.include_router(grow_types_router, prefix=f"{settings.api_prefix}/grow-types", tags=["grow-types"])
    app.include_router(tents_router, prefix=f"{settings.api_prefix}/tents", tags=["tents"])
    app.include_router(quick_log_router, prefix=f"{settings.api_prefix}/quick-log", tags=["quick-log"])
    app.include_router(grows_router, prefix=f"{settings.api_prefix}/grows", tags=["grows"])
    app.include_router(buckets_router, prefix=f"{settings.api_prefix}/buckets", tags=["buckets"])
    app.include_router(sensors_router, prefix=f"{settings.api_prefix}/sensors", tags=["sensors"])
    app.include_router(tent_sensors_router, prefix=f"{settings.api_prefix}/tent-sensors", tags=["tent-sensors"])
    app.include_router(journal_router, prefix=f"{settings.api_prefix}/journal", tags=["journal"])
    app.include_router(photos_router, prefix=f"{settings.api_prefix}/photos", tags=["photos"])
    app.include_router(feeding_router, prefix=f"{settings.api_prefix}/feeding", tags=["feeding"])
    app.include_router(strains_router, prefix=f"{settings.api_prefix}/strains", tags=["strains"])
    app.include_router(yields_router, prefix=f"{settings.api_prefix}/yields", tags=["yields"])
    app.include_router(weather_router, prefix=f"{settings.api_prefix}/weather", tags=["weather"])
    app.include_router(reference_router, prefix=f"{settings.api_prefix}/reference", tags=["reference"])
    app.include_router(ai_router, prefix=f"{settings.api_prefix}/ai", tags=["ai"])
    app.include_router(diagnose_router, prefix=f"{settings.api_prefix}/ai", tags=["ai-diagnosis"])
    app.include_router(conversation_router, prefix=f"{settings.api_prefix}/conversations", tags=["conversations"])
    app.include_router(automation_router, prefix=f"{settings.api_prefix}/automation", tags=["automation"])
    app.include_router(notifications_router, prefix=f"{settings.api_prefix}/notifications", tags=["notifications"])
    app.include_router(internal_alerts_router, tags=["internal"])
    app.include_router(billing_router, prefix=f"{settings.api_prefix}/billing", tags=["billing"])
    app.include_router(billing_plans_router, prefix=f"{settings.api_prefix}/billing/plans", tags=["billing-plans"])
    app.include_router(
        billing_providers_router, prefix=f"{settings.api_prefix}/billing/providers", tags=["billing-providers"]
    )
    app.include_router(billing_cancel_router, prefix=f"{settings.api_prefix}/billing", tags=["billing-cancellation"])
    app.include_router(billing_invoices_router, prefix=f"{settings.api_prefix}/billing", tags=["billing-invoices"])
    app.include_router(billing_metrics_router, prefix=f"{settings.api_prefix}/billing", tags=["billing-metrics"])
    app.include_router(account_deletion_router, prefix=f"{settings.api_prefix}/account", tags=["account"])
    app.include_router(data_router, prefix=f"{settings.api_prefix}/data", tags=["data"])
    app.include_router(
        custom_grow_types_router, prefix=f"{settings.api_prefix}/custom-grow-types", tags=["custom-grow-types"]
    )
    app.include_router(tasks_router, prefix=f"{settings.api_prefix}/tasks", tags=["tasks"])
    app.include_router(audit_router, prefix=f"{settings.api_prefix}/audit", tags=["audit"])
    app.include_router(api_keys_router, prefix=f"{settings.api_prefix}/api-keys", tags=["api-keys"])
    app.include_router(admin_router, prefix=f"{settings.api_prefix}/admin", tags=["admin"])
    app.include_router(config_mgmt_router, prefix=f"{settings.api_prefix}/admin/config", tags=["config-management"])
    app.include_router(plot_router, prefix=f"{settings.api_prefix}/grows", tags=["outdoor-plot"])
    app.include_router(field_canvas_router, prefix=f"{settings.api_prefix}", tags=["field-canvas"])
    app.include_router(soil_router, prefix=f"{settings.api_prefix}/grows", tags=["outdoor-soil"])
    app.include_router(pest_router, prefix=f"{settings.api_prefix}/grows", tags=["outdoor-pest"])
    app.include_router(harvest_yield_router, prefix=f"{settings.api_prefix}/grows", tags=["outdoor-yields"])
    app.include_router(companion_router, prefix=f"{settings.api_prefix}/companion-plants", tags=["companion-plants"])
    app.include_router(intelligence_router, prefix=f"{settings.api_prefix}/outdoor", tags=["outdoor-intelligence"])
    app.include_router(container_router, prefix=f"{settings.api_prefix}/grows", tags=["outdoor-containers"])
    app.include_router(runoff_router, prefix=f"{settings.api_prefix}/grows", tags=["outdoor-runoff"])
    app.include_router(integrations_router, prefix=f"{settings.api_prefix}/integrations", tags=["integrations"])
    app.include_router(equipment_router, prefix=f"{settings.api_prefix}/equipment", tags=["equipment"])
    app.include_router(expense_router, prefix=f"{settings.api_prefix}/grows", tags=["cost-roi"])
    app.include_router(support_tickets_router, prefix=f"{settings.api_prefix}/support/tickets", tags=["support"])
    app.include_router(support_admin_router, prefix=f"{settings.api_prefix}/support/admin", tags=["support-admin"])
    app.include_router(kb_router, prefix=f"{settings.api_prefix}/support/kb", tags=["knowledge-base"])
    app.include_router(forum_router, prefix=f"{settings.api_prefix}/support/forum", tags=["forum"])

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/health/ready")
    async def health_ready():
        """Readiness probe — verifies DB connectivity."""
        from sqlalchemy import text

        from app.database import async_session_factory

        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            return {"status": "ok", "db": "connected"}
        except Exception:
            return JSONResponse(
                status_code=503,
                content={"status": "degraded", "db": "unreachable"},
            )

    @app.get(f"{settings.api_prefix}/status")
    async def system_status():
        """System status — connectivity for Ollama, DB, MQTT, and Gemini."""
        import httpx
        from sqlalchemy import text

        from app.database import async_session_factory

        results: dict = {}

        # Database
        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            results["database"] = "connected"
        except Exception:
            results["database"] = "unreachable"

        # Ollama
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                if resp.status_code == 200:
                    models = [m["name"] for m in resp.json().get("models", [])]
                    results["ollama"] = "connected"
                    results["ollama_models"] = models
                else:
                    results["ollama"] = "error"
        except Exception:
            results["ollama"] = "unreachable"

        # Gemini
        results["gemini"] = "configured" if settings.gemini_api_key else "not_configured"

        # MQTT
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(
                    f"http://{settings.mqtt_broker_host}:18083/api/v5/status",
                )
                results["mqtt"] = "connected" if resp.status_code == 200 else "error"
        except Exception:
            results["mqtt"] = "unreachable"

        overall = "ok" if results["database"] == "connected" else "degraded"
        return {"status": overall, **results}

    return app


app = create_app()
