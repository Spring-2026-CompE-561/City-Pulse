from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import Event


async def list_events_by_region(
    db: AsyncSession, *, region_id: int, skip: int, limit: int
) -> list[Event]:
    result = await db.execute(
        select(Event).where(col(Event.region_id) == region_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_event_by_id(db: AsyncSession, event_id: int) -> Event | None:
    return await db.get(Event, event_id)


async def create_event(
    db: AsyncSession, *, region_id: int, user_id: int, title: str, content: str | None
) -> Event:
    event = Event(
        region_id=region_id,
        user_id=user_id,
        title=title,
        content=content,
        created_at=datetime.now(UTC),
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


async def update_event_fields(
    db: AsyncSession, *, event: Event, title: str | None, content: str | None
) -> None:
    if title is not None:
        event.title = title
    if content is not None:
        event.content = content
    await db.flush()


async def delete_event(db: AsyncSession, *, event: Event) -> None:
    await db.delete(event)
    await db.flush()


async def delete_events_by_user_id(db: AsyncSession, *, user_id: int) -> None:
    await db.execute(delete(Event).where(col(Event.user_id) == user_id))
    await db.flush()
