"""City Pulse - FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app import models  # ensure all models registered with Base before init_db
from app.config import settings
from app.database import init_db
from app.routers import auth, events, interactions, regions, trends, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables and seed regions on startup."""
    await init_db()
    yield


app = FastAPI(
    title="CityPulse",
    description="Users (with city location = san diego only), regions, and events.",
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Auth", "description": "Get Bearer token: POST /api/auth/login with body { \"email\": \"user@example.com\", \"password\": \"their_password\" }. Response gives access_token — use it in Authorize as Bearer <access_token>. GET /me returns the current user when authenticated."},
        {"name": "Users", "description": "List, get, create, update, delete. city_location: only 'san diego'."},
        {"name": "Regions", "description": "List regions; list events and users in a region (id or 'san diego')."},
        {"name": "Events", "description": "List events in a region; create (in user's region), update, delete."},
        {"name": "Trends", "description": "Read-only for users. GET most interacted events by region; POST rebuild list; PUT update with new event/order. Priority: attendance, then comments, then likes."},
        {"name": "Interactions", "description": "GET events with interaction counts; PUT add like/comment/attending; DELETE remove like, comment, or attending."},
    ],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(regions.router)
app.include_router(events.router)
app.include_router(trends.router)
app.include_router(interactions.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return consistent 500 error structure for unhandled exceptions."""
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
        "endpoints": ["/api/auth", "/api/users", "/api/regions", "/api/events", "/api/trends", "/api/interactions"],
    }
