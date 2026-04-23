from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import Event


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
) -> list[Event]:
    query = select(Event).where(col(Event.region_id) == region_id)
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
    query = query.order_by(col(Event.event_start_at), col(Event.created_at).desc())
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_event_by_id(db: AsyncSession, event_id: int) -> Event | None:
    return await db.get(Event, event_id)


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

