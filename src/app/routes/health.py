"""Health API used by integration tests and runtime checks."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
async def health():
    """Simple health payload that does not require database access."""
    return {"status": "ok", "service": "City Pulse API"}
