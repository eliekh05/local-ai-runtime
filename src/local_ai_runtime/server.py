"""
FastAPI application factory — config-driven, zero hardcoded values.
"""

import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware


logger = logging.getLogger("local-ai-runtime")


def create_app(server_config: dict) -> FastAPI:
    """Build the FastAPI app from config dict."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(f"Server starting on {server_config['host']}:{server_config['port']}")
        yield
        logger.info("Server shutting down")

    app = FastAPI(
        title="local-ai-runtime",
        description="Local AI chat runtime — BYOK hybrid inference",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({elapsed:.3f}s)")
        return response

    # CORS — from config only
    cors_origins = server_config.get("cors_origins", [])
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/")
    async def root():
        return RedirectResponse(url="/docs")

    # Routes
    from backend.routes.status import router as status_router
    from backend.routes.models import router as models_router
    from backend.routes.config import router as config_router
    from backend.routes.chat import router as chat_router
    from backend.routes.conversations import router as conversations_router
    from backend.routes.metrics import router as metrics_router

    api_prefix = server_config.get("api_prefix", "")
    app.include_router(status_router, prefix=f"{api_prefix}/status", tags=["status"])
    app.include_router(models_router, prefix=f"{api_prefix}/models", tags=["models"])
    app.include_router(config_router, prefix=f"{api_prefix}/config", tags=["config"])
    app.include_router(chat_router, prefix=f"{api_prefix}/chat", tags=["chat"])
    app.include_router(conversations_router, prefix=f"{api_prefix}/conversations", tags=["conversations"])
    app.include_router(metrics_router, prefix=f"{api_prefix}/metrics", tags=["metrics"])

    return app
