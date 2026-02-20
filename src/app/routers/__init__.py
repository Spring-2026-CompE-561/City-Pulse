"""API routers."""

from app.routers import auth, events, interactions, regions, trends, users

__all__ = ["auth", "users", "regions", "events", "trends", "interactions"]
