"""
City Pulse - FastAPI application entrypoint.

What lives here
- The FastAPI `app` object that an ASGI server imports and runs.
- Startup/lifespan wiring that initializes database tables and seeds the default region.
- Router registration (Auth/Users/Regions/Events/Trends/Interactions).
- A global exception handler for consistent 500 responses.

Called by / import relationships
- Exported by `app/__init__.py` as `app` so external runners can do `from app import app`.
- Routers imported from `app.routers.*` are mounted via `app.include_router(...)`.
- `init_db()` comes from `app.database` and is invoked during application startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import auth, events, interactions, regions, trends, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan hook.

    What it does
    - Runs once on startup to ensure DB schema exists and required seed data exists.
    - Yields control back to FastAPI to run the application.

    Called by
    - FastAPI itself, because `lifespan=lifespan` is passed when instantiating `FastAPI(...)`.
    """
    # Initialize database schema and seed the default region.
    await init_db()
    # Hand control back to FastAPI for the remainder of the app lifecycle.
    yield


app = FastAPI(
    title="CityPulse",
    description="Users (with city location = san diego only), regions, and events.",
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=[
        # These tags group endpoints in the Swagger UI (`/docs`).
        {
            "name": "Auth",
            "description": 'Register: POST /api/auth/register (name, email, password, city_location). Login: POST /api/auth/login (email, password). Both return access_token and refresh_token. Use access_token as Bearer for /me and protected endpoints. Refresh: POST /api/auth/refresh with { "refresh_token": "..." } to get new tokens.',
        },
        {
            "name": "Users",
            "description": "List, get, update, delete. Register via POST /api/auth/register only. city_location: only 'san diego'.",
        },
        {
            "name": "Regions",
            "description": "List regions; list events and users in a region (id or 'san diego').",
        },
        {
            "name": "Events",
            "description": "List events in a region; create (in user's region), update, delete.",
        },
        {
            "name": "Trends",
            "description": "Read-only for users. GET most interacted events by region; POST rebuild list; PUT update with new event/order. Priority: attendance, then comments, then likes.",
        },
        {
            "name": "Interactions",
            "description": "GET events with interaction counts; PUT add like/comment/attending; DELETE remove like, comment, or attending.",
        },
    ],
)

# Mount each feature router under its prefix (declared inside each router module).
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(regions.router)
app.include_router(events.router)
app.include_router(trends.router)
app.include_router(interactions.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global fallback exception handler.

    What it does
    - If something raises an exception that isn't explicitly handled elsewhere,
      this returns a consistent JSON error response: `{ "detail": "...", "success": false }`.
    - If `settings.debug` is enabled, it includes exception type/message in the detail
      to help local debugging.

    Called by
    - FastAPI/Starlette when an exception bubbles up out of a request handler.
    """
    if isinstance(exc, HTTPException):
        # Let FastAPI's default HTTPException handling run as usual.
        raise exc
    # Default message for production: avoid leaking internal details.
    detail = "Internal server error"
    if settings.debug:
        # In debug mode, include exception class/message to speed up troubleshooting.
        detail = f"{type(exc).__name__}: {exc!s}"
    return JSONResponse(
        status_code=500,
        content={"detail": detail, "success": False},
    )


@app.get("/")
async def root():
    """
    Lightweight service discovery endpoint.

    Called by
    - Anyone (no auth). Useful for quick health/manual checks.
    """
    return {
        "service": "City Pulse",
        "docs": "/docs",
        "openapi": "/openapi.json",
        # Convenience list of the high-level API prefixes this backend exposes.
        "endpoints": [
            "/api/auth",
            "/api/users",
            "/api/regions",
            "/api/events",
            "/api/trends",
            "/api/interactions",
        ],
    }
