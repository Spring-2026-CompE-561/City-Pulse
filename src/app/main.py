"""City Pulse FastAPI application."""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes import api_router
from app.config import settings
from app.database import async_session_maker, init_db
from app.ingestion.service import run_ingestion

logger = logging.getLogger("app.request")
# Vercel/AWS Lambda file systems are read-only outside /tmp; mkdir under the bundle fails at import.
_media_candidate = Path(__file__).resolve().parents[1] / "media"
try:
    _media_candidate.mkdir(parents=True, exist_ok=True)
    MEDIA_ROOT = _media_candidate
except OSError:
    MEDIA_ROOT = Path(os.environ.get("TMPDIR", "/tmp")) / "citypulse-media"
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


async def _ingestion_scheduler_loop() -> None:
    interval_seconds = max(settings.ingest_scheduler_interval_minutes, 5) * 60
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            async with async_session_maker() as db:
                await run_ingestion(db, trigger_type="scheduler")
                await db.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Scheduled ingestion run failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_ready = False
    app.state.db_init_error = None
    if not settings.skip_db_init:
        try:
            await init_db()
            app.state.db_ready = True
        except Exception as exc:
            app.state.db_init_error = f"{type(exc).__name__}: {exc}"
            logger.exception("Database initialization failed")
    else:
        app.state.db_ready = True
    scheduler_task: asyncio.Task | None = None
    if settings.ingest_scheduler_enabled and app.state.db_ready:
        scheduler_task = asyncio.create_task(_ingestion_scheduler_loop())
    yield
    if scheduler_task is not None:
        scheduler_task.cancel()
        with suppress(asyncio.CancelledError):
            await scheduler_task


app = FastAPI(
    title="CityPulse",
    description="Users (with city location = san diego only), regions, and events.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="media")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )
    detail = "Internal server error"
    if settings.debug:
        detail = f"{type(exc).__name__}: {exc!s}"
    return JSONResponse(
        status_code=500,
        content={"detail": detail, "success": False},
    )


@app.get("/")
async def root():
    return {
        "service": "City Pulse",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": [
            "/api/auth",
            "/api/users",
            "/api/regions",
            "/api/events",
            "/api/health",
            "/api/trends",
            "/api/interactions",
            "/api/sources",
            "/api/ingest",
            "/api/partner-submissions",
        ],
    }
