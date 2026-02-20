"""Trends API: list most interacted events by region (read-only for users); POST rebuild list, PUT update with new event/order."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Event, EventAttending, EventComment, EventLike, Trend
from app.region_map import parse_region_param
from app.schemas import SuccessResponse, TrendEntryRead, TrendRebuildBody, TrendUpdateBody

router = APIRouter(prefix="/api/trends", tags=["Trends"])


def _order_key(item: tuple) -> tuple:
    """Sort key: 1st attendance, 2nd comments, 3rd likes (all descending)."""
    _event_id, att, com, lik = item
    return (-att, -com, -lik)


@router.get("/", response_model=list[TrendEntryRead])
async def get_trends(
    region: str | int = Query("san diego", description="Region: 'san diego' or 0"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the list of most interacted events in the given region. Ordered by rank (1st attendance, 2nd comments, 3rd likes)."""
    try:
        region_id = parse_region_param(region)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    result = await db.execute(
        select(Trend, Event.title)
        .join(Event, Event.id == Trend.event_id)
        .where(Trend.region_id == region_id)
        .order_by(Trend.rank)
        .offset(skip)
        .limit(limit)
    )
    rows = result.all()
    return [
        TrendEntryRead(
            event_id=t.event_id,
            rank=t.rank,
            title=title,
            attendance_count=t.attendance_count,
            comments_count=t.comments_count,
            likes_count=t.likes_count,
            updated_at=t.updated_at,
        )
        for t, title in rows
    ]


async def _get_event_interaction_counts(db: AsyncSession, region_id: int) -> dict[int, tuple[int, int, int]]:
    """Return map event_id -> (attendance_count, comments_count, likes_count) for all events in region."""
    events_in_region = await db.execute(select(Event.id).where(Event.region_id == region_id))
    event_ids = [r[0] for r in events_in_region.all()]
    if not event_ids:
        return {}

    att = (
        select(EventAttending.event_id, func.count(EventAttending.id).label("c"))
        .where(EventAttending.event_id.in_(event_ids))
        .group_by(EventAttending.event_id)
    )
    com = (
        select(EventComment.event_id, func.count(EventComment.id).label("c"))
        .where(EventComment.event_id.in_(event_ids))
        .group_by(EventComment.event_id)
    )
    lik = (
        select(EventLike.event_id, func.count(EventLike.id).label("c"))
        .where(EventLike.event_id.in_(event_ids))
        .group_by(EventLike.event_id)
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


@router.post("/", status_code=201)
async def rebuild_trends(
    payload: TrendRebuildBody,
    db: AsyncSession = Depends(get_db),
):
    """Build a new trend list for the region from current interaction counts. Order: 1st attendance, 2nd comments, 3rd likes."""
    try:
        region_id = parse_region_param(payload.region)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    counts = await _get_event_interaction_counts(db, region_id)
    if not counts:
        await db.execute(delete(Trend).where(Trend.region_id == region_id))
        await db.flush()
        return {"success": True, "count": 0}

    sorted_events = sorted(
        [(eid, att, com, lik) for eid, (att, com, lik) in counts.items()],
        key=_order_key,
    )
    await db.execute(delete(Trend).where(Trend.region_id == region_id))
    now = datetime.now(timezone.utc)
    for rank, (event_id, att, com, lik) in enumerate(sorted_events, start=1):
        t = Trend(
            region_id=region_id,
            event_id=event_id,
            rank=rank,
            attendance_count=att,
            comments_count=com,
            likes_count=lik,
            updated_at=now,
        )
        db.add(t)
    await db.flush()
    return {"success": True, "count": len(sorted_events)}


@router.put("/", response_model=SuccessResponse)
async def update_trends(
    payload: TrendUpdateBody,
    db: AsyncSession = Depends(get_db),
):
    """Add or update an event in the trend list for the region, then reorder by interactions (attendance, comments, likes)."""
    try:
        region_id = parse_region_param(payload.region)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    event = await db.get(Event, payload.event_id)
    if not event or event.region_id != region_id:
        raise HTTPException(status_code=404, detail="Event not found in this region")

    counts = await _get_event_interaction_counts(db, region_id)
    att, com, lik = counts.get(payload.event_id, (0, 0, 0))

    existing = await db.execute(
        select(Trend).where(Trend.region_id == region_id, Trend.event_id == payload.event_id)
    )
    trend_row = existing.scalar_one_or_none()
    if trend_row:
        trend_row.attendance_count = att
        trend_row.comments_count = com
        trend_row.likes_count = lik
        trend_row.updated_at = datetime.now(timezone.utc)
    else:
        max_rank = await db.execute(
            select(func.coalesce(func.max(Trend.rank), 0)).where(Trend.region_id == region_id)
        )
        next_rank = max_rank.scalar() + 1
        trend_row = Trend(
            region_id=region_id,
            event_id=payload.event_id,
            rank=next_rank,
            attendance_count=att,
            comments_count=com,
            likes_count=lik,
        )
        db.add(trend_row)
    await db.flush()

    all_trends = await db.execute(
        select(Trend).where(Trend.region_id == region_id).order_by(Trend.rank)
    )
    rows = list(all_trends.scalars().all())
    rows.sort(key=lambda t: _order_key((t.event_id, t.attendance_count, t.comments_count, t.likes_count)))
    for rank, t in enumerate(rows, start=1):
        t.rank = rank
    await db.flush()
    return SuccessResponse()
