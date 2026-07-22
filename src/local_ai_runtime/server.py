"""
FastAPI application — serves API + frontend from one package.
"""

import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("local-ai-runtime")

_STATIC_PATH = Path(__file__).parent / "static" / "index.html"


def create_app(server_config: dict) -> FastAPI:
    index_html = _STATIC_PATH.read_text() if _STATIC_PATH.exists() else ""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(f"Server starting on {server_config['host']}:{server_config['port']}")
        yield
        logger.info("Server shutting down")

    try:
        from importlib.metadata import version as pkg_version
        app_version = pkg_version("local-ai-runtime")
    except Exception:
        app_version = "0.1.27"

    app = FastAPI(
        title="local-ai-runtime",
        description="BYOK hybrid local AI chat runtime",
        version=app_version,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({elapsed:.3f}s)")
        return response

    cors_origins = server_config.get("cors_origins", [])
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # API routes
    from backend.routes.status import router as status_router
    from backend.routes.models import router as models_router
    from backend.routes.config import router as config_router
    from backend.routes.chat import router as chat_router
    from backend.routes.conversations import router as conversations_router
    from backend.routes.metrics import router as metrics_router
    from backend.routes.openai_v1 import router as openai_v1_router

    prefix = server_config.get("api_prefix", "")
    app.include_router(status_router, prefix=f"{prefix}/status", tags=["status"])
    app.include_router(models_router, prefix=f"{prefix}/models", tags=["models"])
    app.include_router(config_router, prefix=f"{prefix}/config", tags=["config"])
    app.include_router(chat_router, prefix=f"{prefix}/chat", tags=["chat"])
    app.include_router(conversations_router, prefix=f"{prefix}/conversations", tags=["conversations"])
    app.include_router(metrics_router, prefix=f"{prefix}/metrics", tags=["metrics"])
    # OpenAI-compatible gateway for SDKs / other clients (9router-style)
    app.include_router(openai_v1_router, prefix=f"{prefix}/v1", tags=["openai-v1"])

    # Serve frontend
    if index_html:
        @app.get("/", include_in_schema=False)
        async def root():
            return HTMLResponse(content=index_html)
    else:
        @app.get("/", include_in_schema=False)
        async def root():
            return RedirectResponse(url="/docs")

    return app
