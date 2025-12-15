from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .db import database
from .errors import GatewayError, InternalError
from .routers import day, meals, products, settings as settings_router, stats

logger = logging.getLogger(__name__)

DEFAULT_CORS_ORIGINS = [
    "https://my-miniapp-production.up.railway.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


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

    cors_origins = settings.parsed_cors_origins or DEFAULT_CORS_ORIGINS

    if settings.parsed_cors_origins:
        logger.info("Enabling CORS for origins from settings: %s", cors_origins)
    else:
        logger.warning(
            "CORS_ORIGINS env var is empty; falling back to default origins: %s",
            cors_origins,
        )

    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            # Разрешаем только необходимые методы
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            # Разрешаем только необходимые заголовки
            allow_headers=["Content-Type", "Authorization"],
            allow_credentials=True,
        )
    else:
        logger.error("CORS middleware disabled: no origins configured")

    @app.exception_handler(GatewayError)
    async def gateway_error_handler(request: Request, exc: GatewayError) -> JSONResponse:  # type: ignore[override]
        # Логируем осознанные бизнес-ошибки с кодом и сообщением
        logger.warning("Gateway error [%s] at %s: %s", exc.code, request.url.path, exc.message)
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
        # Логируем полный стектрейс на сервере
        logger.exception("Unhandled error at %s: %s", request.url.path, exc)

        # В проде показываем общее сообщение, в dev/stage — класс и текст ошибки,
        # чтобы в браузере было понятно, что именно пошло не так.
        if settings.is_production():
            internal = InternalError()
        else:
            internal = InternalError(message=f"{exc.__class__.__name__}: {exc}")

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
    app.include_router(settings_router.router, prefix="/v1")
    app.include_router(stats.router, prefix="/v1")

    return app


app = create_app()
