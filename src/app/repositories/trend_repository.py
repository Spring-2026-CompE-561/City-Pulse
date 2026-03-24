from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import Event, Trend
from app.repositories.interaction_repository import get_counts_for_event_ids


async def list_trends_with_event_titles(
    db: AsyncSession, *, region_id: int, skip: int, limit: int
) -> list[tuple[Trend, str]]:
    result = await db.execute(
        select(Trend, col(Event.title))
        .join(Event, col(Event.id) == col(Trend.event_id))
        .where(col(Trend.region_id) == region_id)
        .order_by(col(Trend.rank))
        .offset(skip)
        .limit(limit)
    )
    return [(row[0], row[1]) for row in result.all()]


async def get_event_ids_in_region(db: AsyncSession, *, region_id: int) -> list[int]:
    events_in_region = await db.execute(
        select(col(Event.id)).where(col(Event.region_id) == region_id)
    )
    return [event_id for event_id in events_in_region.scalars().all() if event_id is not None]


async def get_event_interaction_counts_by_region(
    db: AsyncSession, *, region_id: int
) -> dict[int, tuple[int, int, int]]:
    event_ids = await get_event_ids_in_region(db, region_id=region_id)
    return await get_counts_for_event_ids(db, event_ids=event_ids)


async def clear_region_trends(db: AsyncSession, *, region_id: int) -> None:
    await db.execute(delete(Trend).where(col(Trend.region_id) == region_id))
    await db.flush()


async def create_trend_row(
    db: AsyncSession,
    *,
    region_id: int,
    event_id: int,
    rank: int,
    attendance_count: int,
    comments_count: int,
    likes_count: int,
    updated_at: datetime | None = None,
) -> Trend:
    trend = Trend(
        region_id=region_id,
        event_id=event_id,
        rank=rank,
        attendance_count=attendance_count,
        comments_count=comments_count,
        likes_count=likes_count,
        updated_at=updated_at if updated_at is not None else datetime.utcnow(),
    )
    db.add(trend)
    return trend


async def get_trend_for_region_event(
    db: AsyncSession, *, region_id: int, event_id: int
) -> Trend | None:
    existing = await db.execute(
        select(Trend).where(
            col(Trend.region_id) == region_id,
            col(Trend.event_id) == event_id,
        )
    )
    return existing.scalar_one_or_none()


async def get_next_rank_for_region(db: AsyncSession, *, region_id: int) -> int:
    max_rank = await db.execute(
        select(func.coalesce(func.max(Trend.rank), 0)).where(col(Trend.region_id) == region_id)
    )
    current = max_rank.scalar() or 0
    return current + 1


async def list_trends_for_region(db: AsyncSession, *, region_id: int) -> list[Trend]:
    result = await db.execute(
        select(Trend).where(col(Trend.region_id) == region_id).order_by(col(Trend.rank))
    )
    return list(result.scalars().all())


async def flush(db: AsyncSession) -> None:
    await db.flush()
