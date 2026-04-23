from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import EventAttending, EventComment, EventLike


async def get_like(
    db: AsyncSession, *, event_id: int, user_id: int
) -> EventLike | None:
    result = await db.execute(
        select(EventLike).where(
            col(EventLike.event_id) == event_id,
            col(EventLike.user_id) == user_id,
        )
    )
    return result.scalar_one_or_none()


async def add_like(db: AsyncSession, *, event_id: int, user_id: int) -> None:
    like = EventLike(event_id=event_id, user_id=user_id)
    db.add(like)
    await db.flush()


async def remove_like(db: AsyncSession, *, like: EventLike) -> None:
    await db.delete(like)
    await db.flush()


async def add_comment(
    db: AsyncSession, *, event_id: int, user_id: int, text: str
) -> EventComment:
    comment = EventComment(
        event_id=event_id,
        user_id=user_id,
        text=text,
        created_at=datetime.now(UTC),
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


async def get_comment_by_id(db: AsyncSession, *, comment_id: int) -> EventComment | None:
    return await db.get(EventComment, comment_id)


async def list_comments_for_event(db: AsyncSession, *, event_id: int) -> list[EventComment]:
    comments_result = await db.execute(
        select(EventComment)
        .where(col(EventComment.event_id) == event_id)
        .order_by(col(EventComment.created_at))
    )
    return list(comments_result.scalars().all())


async def remove_comment(db: AsyncSession, *, comment: EventComment) -> None:
    await db.delete(comment)
    await db.flush()


async def get_attending(
    db: AsyncSession, *, event_id: int, user_id: int
) -> EventAttending | None:
    result = await db.execute(
        select(EventAttending).where(
            col(EventAttending.event_id) == event_id,
            col(EventAttending.user_id) == user_id,
        )
    )
    return result.scalar_one_or_none()


async def add_attending(db: AsyncSession, *, event_id: int, user_id: int) -> None:
    attending = EventAttending(event_id=event_id, user_id=user_id)
    db.add(attending)
    await db.flush()


async def remove_attending(db: AsyncSession, *, attending: EventAttending) -> None:
    await db.delete(attending)
    await db.flush()


async def get_event_interaction_counts(
    db: AsyncSession, *, event_id: int
) -> tuple[int, int, int]:
    likes_count_result = await db.execute(
        select(func.count(col(EventLike.id))).where(col(EventLike.event_id) == event_id)
    )
    comments_count_result = await db.execute(
        select(func.count(col(EventComment.id))).where(col(EventComment.event_id) == event_id)
    )
    attendance_count_result = await db.execute(
        select(func.count(col(EventAttending.id))).where(col(EventAttending.event_id) == event_id)
    )
    return (
        likes_count_result.scalar() or 0,
        comments_count_result.scalar() or 0,
        attendance_count_result.scalar() or 0,
    )


async def get_counts_for_event_ids(
    db: AsyncSession, *, event_ids: list[int]
) -> dict[int, tuple[int, int, int]]:
    if not event_ids:
        return {}

    att = (
        select(col(EventAttending.event_id), func.count(col(EventAttending.id)).label("c"))
        .where(col(EventAttending.event_id).in_(event_ids))
        .group_by(col(EventAttending.event_id))
    )
    com = (
        select(col(EventComment.event_id), func.count(col(EventComment.id)).label("c"))
        .where(col(EventComment.event_id).in_(event_ids))
        .group_by(col(EventComment.event_id))
    )
    lik = (
        select(col(EventLike.event_id), func.count(col(EventLike.id)).label("c"))
        .where(col(EventLike.event_id).in_(event_ids))
        .group_by(col(EventLike.event_id))
    )
    r_att = await db.execute(att)
    r_com = await db.execute(com)
    r_lik = await db.execute(lik)
    by_event_att = {row[0]: row[1] for row in r_att.all()}
    by_event_com = {row[0]: row[1] for row in r_com.all()}
    by_event_lik = {row[0]: row[1] for row in r_lik.all()}

    return {
        eid: (
            by_event_att.get(eid, 0),
            by_event_com.get(eid, 0),
            by_event_lik.get(eid, 0),
        )
        for eid in event_ids
    }

