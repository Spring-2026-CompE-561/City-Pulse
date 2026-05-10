"""Health API used by integration tests and runtime checks."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
async def health(request: Request):
    """Liveness + whether DB migrations ran (startup)."""
    if settings.skip_db_init:
        return {"status": "ok", "service": "City Pulse API", "database": "skipped"}
    if getattr(request.app.state, "db_ready", False):
        return {"status": "ok", "service": "City Pulse API", "database": "ready"}
    err = getattr(request.app.state, "db_init_error", None)
    payload: dict = {
        "status": "degraded",
        "service": "City Pulse API",
        "database": "unavailable",
    }
    if settings.debug and err:
        payload["detail"] = err
    return JSONResponse(status_code=503, content=payload)
