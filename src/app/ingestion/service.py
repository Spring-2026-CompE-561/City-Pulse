from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.adapters import fetch_source_events
from app.ingestion.upsert_service import upsert_normalized_event
from app.models import Source
from app.region_map import REGION_SAN_DIEGO_ID
from app.repositories.ingest_repository import complete_ingest_run, create_ingest_run
from app.repositories.source_repository import get_source_by_id, list_active_sources
from app.repositories.trend_repository import (
    clear_region_trends,
    create_trend_row,
    flush as flush_trends,
    get_event_interaction_counts_by_region,
)


async def _sources_for_run(
    db: AsyncSession,
    *,
    region_id: int,
    source_id: int | None,
    area: str | None,
) -> list[Source]:
    if source_id is not None:
        source = await get_source_by_id(db, source_id)
        if source is None or not source.is_active:
            return []
        if area and source.neighborhood and source.neighborhood != area:
            return []
        return [source]
    return await list_active_sources(db, region_id=region_id, neighborhood=area)


async def run_ingestion(
    db: AsyncSession,
    *,
    source_id: int | None = None,
    area: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    trigger_type: str = "manual",
) -> dict[str, int | str]:
    region_id = REGION_SAN_DIEGO_ID
    run = await create_ingest_run(
        db, region_id=region_id, source_id=source_id, trigger_type=trigger_type, area=area
    )
    fetched_count = 0
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    error_messages: list[str] = []

    sources = await _sources_for_run(db, region_id=region_id, source_id=source_id, area=area)
    for source in sources:
        if not source.crawl_allowed:
            skipped_count += 1
            continue
        try:
            items = await fetch_source_events(
                source, start_date=start_date, end_date=end_date
            )
        except Exception as exc:  # noqa: BLE001
            error_count += 1
            error_messages.append(f"{source.name}: {exc!s}")
            continue
        fetched_count += len(items)
        for item in items:
            try:
                outcome = await upsert_normalized_event(db, region_id=region_id, normalized=item)
            except Exception as exc:  # noqa: BLE001
                error_count += 1
                error_messages.append(f"{source.name}/{item.title}: {exc!s}")
                continue
            if outcome == "inserted":
                inserted_count += 1
            else:
                updated_count += 1

    status = "success" if error_count == 0 else "partial_failure"
    if not sources:
        status = "no_sources"
    await complete_ingest_run(
        db,
        run=run,
        status=status,
        fetched_count=fetched_count,
        inserted_count=inserted_count,
        updated_count=updated_count,
        skipped_count=skipped_count,
        error_count=error_count,
        error_summary=" | ".join(error_messages[:5]) if error_messages else None,
    )
    await _rebuild_trends_for_region(db, region_id=region_id)
    return {
        "status": status,
        "fetched_count": fetched_count,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
    }


def _order_key(item: tuple[int, int, int, int]) -> tuple[int, int, int]:
    _, att, com, lik = item
    return (-att, -com, -lik)


async def _rebuild_trends_for_region(db: AsyncSession, *, region_id: int) -> None:
    counts = await get_event_interaction_counts_by_region(db, region_id=region_id)
    sorted_events = sorted(
        [(event_id, att, com, lik) for event_id, (att, com, lik) in counts.items()],
        key=_order_key,
    )
    await clear_region_trends(db, region_id=region_id)
    for rank, (event_id, att, com, lik) in enumerate(sorted_events, start=1):
        await create_trend_row(
            db,
            region_id=region_id,
            event_id=event_id,
            rank=rank,
            attendance_count=att,
            comments_count=com,
            likes_count=lik,
        )
    await flush_trends(db)
