"""Trends API: list most interacted events by region (read-only for users); POST rebuild list, PUT update with new event/order."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.event_repository import get_event_by_id
from app.repositories.trend_repository import (
    clear_region_trends,
    create_trend_row,
    flush as flush_repo,
    get_event_interaction_counts_by_region,
    get_next_rank_for_region,
    get_trend_for_region_event,
    list_trends_for_region,
    list_trends_with_event_titles,
)
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
    rows = await list_trends_with_event_titles(db, region_id=region_id, skip=skip, limit=limit)
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
    counts = await get_event_interaction_counts_by_region(db, region_id=region_id)
    if not counts:
        await clear_region_trends(db, region_id=region_id)
        return {"success": True, "count": 0}

    sorted_events = sorted(
        [(eid, att, com, lik) for eid, (att, com, lik) in counts.items()],
        key=_order_key,
    )
    await clear_region_trends(db, region_id=region_id)
    now = datetime.now(timezone.utc)
    for rank, (event_id, att, com, lik) in enumerate(sorted_events, start=1):
        await create_trend_row(
            db,
            region_id=region_id,
            event_id=event_id,
            rank=rank,
            attendance_count=att,
            comments_count=com,
            likes_count=lik,
            updated_at=now,
        )
    await flush_repo(db)
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
    event = await get_event_by_id(db, payload.event_id)
    if not event or event.region_id != region_id:
        raise HTTPException(status_code=404, detail="Event not found in this region")

    counts = await get_event_interaction_counts_by_region(db, region_id=region_id)
    att, com, lik = counts.get(payload.event_id, (0, 0, 0))

    trend_row = await get_trend_for_region_event(
        db, region_id=region_id, event_id=payload.event_id
    )
    if trend_row:
        trend_row.attendance_count = att
        trend_row.comments_count = com
        trend_row.likes_count = lik
        trend_row.updated_at = datetime.now(timezone.utc)
    else:
        next_rank = await get_next_rank_for_region(db, region_id=region_id)
        await create_trend_row(
            db,
            region_id=region_id,
            event_id=payload.event_id,
            rank=next_rank,
            attendance_count=att,
            comments_count=com,
            likes_count=lik,
        )
    await flush_repo(db)

    rows = await list_trends_for_region(db, region_id=region_id)
    rows.sort(key=lambda t: _order_key((t.event_id, t.attendance_count, t.comments_count, t.likes_count)))
    for rank, t in enumerate(rows, start=1):
        t.rank = rank
    await flush_repo(db)
    return SuccessResponse()
