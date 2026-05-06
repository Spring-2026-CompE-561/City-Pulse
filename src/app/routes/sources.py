"""Source registry APIs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_ingest_api_key
from app.database import get_db
from app.region_map import REGION_SAN_DIEGO_ID
from app.repository.source import get_source_by_id, list_active_sources
from app.schemas import SourceRead

router = APIRouter(prefix="/api/sources", tags=["Sources"])


@router.get("/", response_model=list[SourceRead])
async def list_sources(
    neighborhood: str | None = Query(default=None),
    category: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    _auth: None = Depends(require_ingest_api_key),
    db: AsyncSession = Depends(get_db),
):
    if include_inactive:
        raise HTTPException(
            status_code=400,
            detail="Inactive listing is not available in this endpoint.",
        )
    return await list_active_sources(
        db,
        region_id=REGION_SAN_DIEGO_ID,
        category_hint=category,
        neighborhood=neighborhood,
    )


@router.get("/{source_id}", response_model=SourceRead)
async def get_source(
    source_id: int,
    _auth: None = Depends(require_ingest_api_key),
    db: AsyncSession = Depends(get_db),
):
    source = await get_source_by_id(db, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source
