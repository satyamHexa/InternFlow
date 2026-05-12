from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.database import engine
from app.core.logging_config import configure_logging
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.rate_limiter import limiter

logger = logging.getLogger("internflow")


# ── Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging(settings.LOG_LEVEL)
    logger.info(
        "InternFlow starting | version=%s env=%s",
        settings.APP_VERSION,
        settings.APP_ENV,
    )
    yield
    await engine.dispose()
    logger.info("InternFlow shutdown complete")


# ── Application factory ─────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-assisted internship referral and onboarding automation platform",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
        lifespan=lifespan,
    )

    # ── Rate limiter state ──────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Middleware stack (applied in reverse order) ────────────────────
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────
    _register_routers(app)

    # ── Global exception handler ────────────────────────────────────
    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    # ── Health endpoint ───────────────────────────────────────────
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {
            "status": "ok",
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        }

    return app


def _register_routers(app: FastAPI) -> None:
    from app.api.auth.routes import router as auth_router
    from app.api.users.routes import router as users_router
    from app.api.referral.routes import router as referral_router
    from app.api.workflow.routes import router as workflow_router
    from app.api.dashboard.routes import router as dashboard_router
    from app.api.notifications.routes import router as notifications_router
    from app.api.onboarding.routes import router as onboarding_router
    from app.api.certificates.routes import router as certificates_router
    from app.api.audit.routes import router as audit_router
    from app.api.ai.routes import router as ai_router

    prefix = "/api/v1"
    app.include_router(auth_router,          prefix=f"{prefix}/auth",          tags=["Authentication"])
    app.include_router(users_router,         prefix=f"{prefix}/users",         tags=["Users"])
    app.include_router(referral_router,      prefix=f"{prefix}/referrals",      tags=["Referrals"])
    app.include_router(workflow_router,      prefix=f"{prefix}/workflow",        tags=["Workflow"])
    app.include_router(dashboard_router,     prefix=f"{prefix}/dashboard",       tags=["Dashboard"])
    app.include_router(notifications_router, prefix=f"{prefix}/notifications",   tags=["Notifications"])
    app.include_router(onboarding_router,    prefix=f"{prefix}/onboarding",      tags=["Onboarding"])
    app.include_router(certificates_router,  prefix=f"{prefix}/certificates",    tags=["Certificates"])
    app.include_router(audit_router,         prefix=f"{prefix}/audit",           tags=["Audit"])
    app.include_router(ai_router,            prefix=f"{prefix}/ai",              tags=["AI"])


# Module-level app instance for uvicorn
app = create_app()
