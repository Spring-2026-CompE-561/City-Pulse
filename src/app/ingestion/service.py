from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.adapters import fetch_source_events
from app.ingestion.upsert_service import upsert_normalized_event
from app.models import Source
from app.region_map import REGION_SAN_DIEGO_ID
from app.repository.ingest import complete_ingest_run, create_ingest_run
from app.repository.event import delete_bad_calendar_events
from app.repository.source import get_source_by_id, list_active_sources
from app.repository.trend import (
    clear_region_trends,
    create_trend_row,
    flush as flush_trends,
    get_event_interaction_counts_by_region,
)


_CALENDAR_TITLE_TOKENS = (
    "calendar",
    "all events",
    "upcoming events",
    "event calendar",
)


def _resolve_ingestion_window(
    start_date: datetime | None,
    end_date: datetime | None,
) -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    window_start = start_date or now
    window_end = end_date or (window_start + timedelta(days=30))
    if window_end < window_start:
        window_end = window_start + timedelta(days=30)
    return window_start, window_end


def _is_calendar_like_item(title: str, content: str | None) -> bool:
    blob = f"{title} {content or ''}".lower()
    return any(token in blob for token in _CALENDAR_TITLE_TOKENS)


def _should_skip_item_for_ingestion(
    item_title: str,
    *,
    has_venue: bool,
    event_start_at: datetime | None,
    content: str | None,
    window_start: datetime,
    window_end: datetime,
) -> bool:
    if not item_title.strip():
        return True
    if not has_venue:
        return True
    if _is_calendar_like_item(item_title, content):
        return True
    if event_start_at is None:
        return True
    return not (window_start <= event_start_at <= window_end)


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


def _short_err(exc: BaseException, *, limit: int = 140) -> str:
    """Keep ingest run row and error_summary columns under legacy VARCHAR limits."""
    text = str(exc)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _join_errors_for_db(messages: list[str], *, max_chars: int = 200) -> str | None:
    if not messages:
        return None
    joined = " | ".join(messages[:5])
    if len(joined) <= max_chars:
        return joined
    return joined[: max_chars - 3].rstrip() + "..."


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
    window_start, window_end = _resolve_ingestion_window(start_date, end_date)
    run = await create_ingest_run(
        db, region_id=region_id, source_id=source_id, trigger_type=trigger_type, area=area
    )
    fetched_count = 0
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    error_messages: list[str] = []
    skipped_count += await delete_bad_calendar_events(db, region_id=region_id)

    sources = await _sources_for_run(db, region_id=region_id, source_id=source_id, area=area)
    for source in sources:
        if not source.crawl_allowed:
            skipped_count += 1
            continue
        source_label = source.name
        try:
            items = await fetch_source_events(
                source, start_date=window_start, end_date=window_end
            )
        except Exception as exc:  # noqa: BLE001
            error_count += 1
            error_messages.append(f"{source_label}: {_short_err(exc)}")
            continue
        fetched_count += len(items)
        for item in items:
            item_title = (item.title[:72] + "…") if item.title and len(item.title) > 72 else (item.title or "?")
            if _should_skip_item_for_ingestion(
                item.title or "",
                has_venue=bool(item.venue_name and item.venue_name.strip()),
                event_start_at=item.event_start_at,
                content=item.content,
                window_start=window_start,
                window_end=window_end,
            ):
                skipped_count += 1
                continue
            try:
                async with db.begin_nested():
                    outcome = await upsert_normalized_event(
                        db, region_id=region_id, normalized=item
                    )
            except Exception as exc:  # noqa: BLE001
                error_count += 1
                error_messages.append(f"{source_label}/{item_title}: {_short_err(exc)}")
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
        error_summary=_join_errors_for_db(error_messages),
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
