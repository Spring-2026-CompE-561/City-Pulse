"""City Pulse route modules."""

from app.routes import (
    auth,
    events,
    health,
    ingest,
    interactions,
    partner_submissions,
    regions,
    sources,
    trends,
    users,
)

__all__ = [
    "auth",
    "users",
    "regions",
    "events",
    "health",
    "trends",
    "interactions",
    "sources",
    "ingest",
    "partner_submissions",
]

