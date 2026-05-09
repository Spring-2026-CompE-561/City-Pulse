from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import col

from app.ingestion.dedupe import build_content_signature
from app.models import Event, Trend


async def list_events_by_region(
    db: AsyncSession,
    *,
    region_id: int,
    skip: int,
    limit: int,
    category: str | None = None,
    neighborhood: str | None = None,
    starts_after: datetime | None = None,
    starts_before: datetime | None = None,
    active_after: datetime | None = None,
) -> list[Event]:
    query = select(Event).where(col(Event.region_id) == region_id).options(joinedload(Event.user))
    if category is not None:
        query = query.where(col(Event.category) == category)
    if neighborhood is not None:
        query = query.where(col(Event.neighborhood) == neighborhood)
    if starts_after is not None:
        query = query.where(
            (col(Event.event_start_at).is_(None)) | (col(Event.event_start_at) >= starts_after)
        )
    if starts_before is not None:
        query = query.where(
            (col(Event.event_start_at).is_(None)) | (col(Event.event_start_at) <= starts_before)
        )
    if active_after is not None:
        query = query.where(
            (col(Event.event_start_at).is_(None))
            | (func.coalesce(col(Event.event_end_at), col(Event.event_start_at)) >= active_after)
        )
    query = query.order_by(col(Event.event_start_at), col(Event.created_at).desc())
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_event_by_id(db: AsyncSession, event_id: int) -> Event | None:
    result = await db.execute(
        select(Event)
        .where(col(Event.id) == event_id)
        .options(joinedload(Event.user), joinedload(Event.source))
    )
    return result.scalar_one_or_none()


async def create_event(
    db: AsyncSession,
    *,
    region_id: int,
    user_id: int | None,
    title: str,
    category: str,
    content: str | None,
    source_id: int | None = None,
    origin_type: str = "user",
    external_id: str | None = None,
    external_url: str | None = None,
    canonical_url: str | None = None,
    event_image_url: str | None = None,
    event_start_at: datetime | None = None,
    event_end_at: datetime | None = None,
    timezone: str = "America/Los_Angeles",
    venue_name: str | None = None,
    venue_address: str | None = None,
    neighborhood: str | None = None,
    city: str = "San Diego",
    price_info: str | None = None,
    promo_summary: str | None = None,
    tags_json: str | None = None,
    source_confidence: float | None = None,
    last_seen_at: datetime | None = None,
) -> Event:
    event = Event(
        region_id=region_id,
        user_id=user_id,
        title=title,
        category=category,
        content=content,
        source_id=source_id,
        origin_type=origin_type,
        external_id=external_id,
        external_url=external_url,
        canonical_url=canonical_url,
        event_image_url=event_image_url,
        event_start_at=event_start_at,
        event_end_at=event_end_at,
        timezone=timezone,
        venue_name=venue_name,
        venue_address=venue_address,
        neighborhood=neighborhood,
        city=city,
        price_info=price_info,
        promo_summary=promo_summary,
        tags_json=tags_json,
        source_confidence=source_confidence,
        last_seen_at=last_seen_at,
        created_at=datetime.now(UTC),
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


async def update_event_fields(
    db: AsyncSession,
    *,
    event: Event,
    title: str | None,
    category: str | None,
    content: str | None,
    event_image_url: str | None = None,
    event_start_at: datetime | None = None,
    event_end_at: datetime | None = None,
    timezone: str | None = None,
    venue_name: str | None = None,
    venue_address: str | None = None,
    neighborhood: str | None = None,
    price_info: str | None = None,
    promo_summary: str | None = None,
    source_confidence: float | None = None,
    last_seen_at: datetime | None = None,
) -> None:
    if title is not None:
        event.title = title
    if category is not None:
        event.category = category
    if content is not None:
        event.content = content
    if event_image_url is not None:
        event.event_image_url = event_image_url
    if event_start_at is not None:
        event.event_start_at = event_start_at
    if event_end_at is not None:
        event.event_end_at = event_end_at
    if timezone is not None:
        event.timezone = timezone
    if venue_name is not None:
        event.venue_name = venue_name
    if venue_address is not None:
        event.venue_address = venue_address
    if neighborhood is not None:
        event.neighborhood = neighborhood
    if price_info is not None:
        event.price_info = price_info
    if promo_summary is not None:
        event.promo_summary = promo_summary
    if source_confidence is not None:
        event.source_confidence = source_confidence
    if last_seen_at is not None:
        event.last_seen_at = last_seen_at
    await db.flush()


async def delete_event(db: AsyncSession, *, event: Event) -> None:
    await db.delete(event)
    await db.flush()


async def delete_events_by_user_id(db: AsyncSession, *, user_id: int) -> None:
    await db.execute(delete(Event).where(col(Event.user_id) == user_id))
    await db.flush()


async def delete_bad_calendar_events(db: AsyncSession, *, region_id: int) -> int:
    """Delete known bad calendar/listing ingest rows that should never render as events."""
    matching_ids_result = await db.execute(
        select(col(Event.id)).where(
            col(Event.region_id) == region_id,
            col(Event.origin_type) == "source",
            (
                func.lower(col(Event.title)).like("%north park observatory calendar%")
                | func.lower(col(Event.title)).like("%upcoming events%")
                | func.lower(col(Event.title)).like("%all events%")
            ),
        )
    )
    matching_ids = [event_id for event_id in matching_ids_result.scalars().all() if event_id is not None]
    if not matching_ids:
        return 0
    await db.execute(delete(Trend).where(col(Trend.event_id).in_(matching_ids)))
    result = await db.execute(delete(Event).where(col(Event.id).in_(matching_ids)))
    await db.flush()
    return int(result.rowcount or 0)


async def remove_duplicate_source_events(db: AsyncSession, *, region_id: int) -> int:
    """Keep one source event per content signature and delete duplicates."""
    result = await db.execute(
        select(Event).where(
            col(Event.region_id) == region_id,
            col(Event.origin_type) == "source",
        )
    )
    events = list(result.scalars().all())
    events.sort(
        key=lambda event: (
            event.last_seen_at or event.created_at,
            event.created_at,
            event.id or 0,
        ),
        reverse=True,
    )

    seen_signatures: set[str] = set()
    duplicate_ids: list[int] = []
    for event in events:
        signature = build_content_signature(
            title=event.title,
            content=event.content,
            venue_name=event.venue_name,
            neighborhood=event.neighborhood,
            event_start_iso=event.event_start_at.isoformat() if event.event_start_at else None,
        )
        if signature in seen_signatures:
            if event.id is not None:
                duplicate_ids.append(event.id)
            continue
        seen_signatures.add(signature)

    if not duplicate_ids:
        return 0

    await db.execute(delete(Trend).where(col(Trend.event_id).in_(duplicate_ids)))
    deletion = await db.execute(delete(Event).where(col(Event.id).in_(duplicate_ids)))
    await db.flush()
    return int(deletion.rowcount or 0)


async def delete_past_events_older_than(
    db: AsyncSession,
    *,
    region_id: int,
    retention_cutoff: datetime,
) -> int:
    """Delete ended events older than the retention cutoff."""
    matching_ids_result = await db.execute(
        select(col(Event.id)).where(
            col(Event.region_id) == region_id,
            col(Event.event_start_at).is_not(None),
            func.coalesce(col(Event.event_end_at), col(Event.event_start_at)) < retention_cutoff,
        )
    )
    matching_ids = [event_id for event_id in matching_ids_result.scalars().all() if event_id is not None]
    if not matching_ids:
        return 0
    await db.execute(delete(Trend).where(col(Trend.event_id).in_(matching_ids)))
    deletion = await db.execute(delete(Event).where(col(Event.id).in_(matching_ids)))
    await db.flush()
    return int(deletion.rowcount or 0)

