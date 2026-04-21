"""Ingestion API for source crawling and run visibility."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_ingest_api_key
from app.database import get_db
from app.ingestion.service import run_ingestion
from app.region_map import REGION_SAN_DIEGO_ID
from app.repositories.ingest_repository import list_ingest_runs
from app.schemas import IngestRunRead, IngestRunRequest

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])


@router.post("/run")
async def run_ingest_job(
    payload: IngestRunRequest,
    _auth: None = Depends(require_ingest_api_key),
    db: AsyncSession = Depends(get_db),
):
    return await run_ingestion(
        db,
        source_id=payload.source_id,
        area=payload.area,
        start_date=payload.start_date,
        end_date=payload.end_date,
        trigger_type="manual",
    )


@router.post("/run-all")
async def run_ingest_all(
    area: str | None = Query(default=None),
    _auth: None = Depends(require_ingest_api_key),
    db: AsyncSession = Depends(get_db),
):
    return await run_ingestion(db, area=area, trigger_type="manual")


@router.get("/runs", response_model=list[IngestRunRead])
async def get_ingest_runs(
    limit: int = Query(20, ge=1, le=100),
    _auth: None = Depends(require_ingest_api_key),
    db: AsyncSession = Depends(get_db),
):
    return await list_ingest_runs(db, region_id=REGION_SAN_DIEGO_ID, limit=limit)
