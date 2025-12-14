from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .db import database
from .errors import GatewayError, InternalError
from .routers import day, meals, products, settings, stats

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    docs_url = "/docs" if settings.enable_docs else None
    redoc_url = "/redoc" if settings.enable_docs else None
    openapi_url = "/openapi.json" if settings.enable_docs else None

    app = FastAPI(
        title="FoodTracker Gateway API",
        version="1.0.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    app.state.settings = settings

    if settings.parsed_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.parsed_cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=False,
        )

    @app.exception_handler(GatewayError)
    async def gateway_error_handler(_: Request, exc: GatewayError) -> JSONResponse:  # type: ignore[override]
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
        logger.exception("Unhandled error: %s", exc)
        internal = InternalError()
        return JSONResponse(status_code=internal.status_code, content=internal.detail)

    @app.get("/healthz")
    async def healthz() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/readyz")
    async def readyz() -> dict[str, bool]:
        try:
            pool = await database.get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
        except Exception as exc:  # pragma: no cover - health endpoint
            logger.exception("Readiness probe failed", exc)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="database unavailable")
        return {"ok": True}

    app.include_router(day.router, prefix="/v1")
    app.include_router(meals.router, prefix="/v1")
    app.include_router(products.router, prefix="/v1")
    app.include_router(settings.router, prefix="/v1")
    app.include_router(stats.router, prefix="/v1")

    return app


app = create_app()
