"""Aggregate router for API v1 endpoints."""

from fastapi import APIRouter

from app.routes import auth, events, interactions, regions, trends, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(regions.router)
api_router.include_router(events.router)
api_router.include_router(trends.router)
api_router.include_router(interactions.router)

