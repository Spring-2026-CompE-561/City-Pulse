from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import IngestRun


async def create_ingest_run(
    db: AsyncSession,
    *,
    region_id: int,
    source_id: int | None,
    trigger_type: str,
    area: str | None,
) -> IngestRun:
    run = IngestRun(
        region_id=region_id,
        source_id=source_id,
        trigger_type=trigger_type,
        area=area,
        status="running",
        started_at=datetime.now(UTC),
    )
    db.add(run)
    await db.flush()
    await db.refresh(run)
    return run


async def complete_ingest_run(
    db: AsyncSession,
    *,
    run: IngestRun,
    status: str,
    fetched_count: int,
    inserted_count: int,
    updated_count: int,
    skipped_count: int,
    error_count: int,
    error_summary: str | None = None,
) -> IngestRun:
    run.status = status
    run.fetched_count = fetched_count
    run.inserted_count = inserted_count
    run.updated_count = updated_count
    run.skipped_count = skipped_count
    run.error_count = error_count
    run.error_summary = error_summary
    run.completed_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(run)
    return run


async def list_ingest_runs(
    db: AsyncSession,
    *,
    region_id: int,
    limit: int = 20,
) -> list[IngestRun]:
    result = await db.execute(
        select(IngestRun)
        .where(col(IngestRun.region_id) == region_id)
        .order_by(col(IngestRun.started_at).desc())
        .limit(limit)
    )
    return list(result.scalars().all())
