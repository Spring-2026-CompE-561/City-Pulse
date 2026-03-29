"""City Pulse FastAPI application."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import api_router
from app.config import settings
from app.database import init_db

logger = logging.getLogger("app.request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


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
            "/api/trends",
            "/api/interactions",
        ],
    }
