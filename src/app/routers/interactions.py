"""Interactions API: list events with interactions; add/remove likes, comments, attending."""

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Event, EventAttending, EventComment, EventLike
from app.region_map import parse_region_param
from app.schemas import (
    CommentRead,
    EventWithInteractionsRead,
    InteractionAttendingBody,
    InteractionCommentBody,
    InteractionLikeBody,
    SuccessResponse,
)

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])


@router.get("/", response_model=list[EventWithInteractionsRead])
async def list_events_with_interactions(
    region: str | int = Query("san diego", description="Region: 'san diego' or 0"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List events in the given region with interaction counts and comments for each event."""
    try:
        region_id = parse_region_param(region)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    result = await db.execute(
        select(Event).where(Event.region_id == region_id).offset(skip).limit(limit)
    )
    events = list(result.scalars().all())
    out = []
    for ev in events:
        likes_count = await db.execute(
            select(func.count(EventLike.id)).where(EventLike.event_id == ev.id)
        )
        comments_count = await db.execute(
            select(func.count(EventComment.id)).where(EventComment.event_id == ev.id)
        )
        attendance_count = await db.execute(
            select(func.count(EventAttending.id)).where(EventAttending.event_id == ev.id)
        )
        comments_result = await db.execute(
            select(EventComment).where(EventComment.event_id == ev.id).order_by(EventComment.created_at)
        )
        comments = list(comments_result.scalars().all())
        out.append(
            EventWithInteractionsRead(
                id=ev.id,
                region_id=ev.region_id,
                user_id=ev.user_id,
                title=ev.title,
                content=ev.content,
                created_at=ev.created_at,
                likes_count=likes_count.scalar() or 0,
                comments_count=comments_count.scalar() or 0,
                attendance_count=attendance_count.scalar() or 0,
                comments=[CommentRead.model_validate(c) for c in comments],
            )
        )
    return out


@router.put("/events/{event_id}/likes", response_model=SuccessResponse)
async def add_like(
    event_id: int = Path(..., description="Event ID"),
    payload: InteractionLikeBody = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Add a like from a user to an event (idempotent: already liked is success)."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing = await db.execute(
        select(EventLike).where(EventLike.event_id == event_id, EventLike.user_id == payload.user_id)
    )
    if existing.scalar_one_or_none():
        return SuccessResponse()
    like = EventLike(event_id=event_id, user_id=payload.user_id)
    db.add(like)
    await db.flush()
    return SuccessResponse()


@router.put("/events/{event_id}/comments", response_model=CommentRead, status_code=201)
async def add_comment(
    event_id: int = Path(..., description="Event ID"),
    payload: InteractionCommentBody = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment from a user to an event."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    comment = EventComment(
        event_id=event_id,
        user_id=payload.user_id,
        text=payload.text,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


@router.put("/events/{event_id}/attending", response_model=SuccessResponse)
async def add_attending(
    event_id: int = Path(..., description="Event ID"),
    payload: InteractionAttendingBody = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Add attendance: user marks they are attending the event (idempotent)."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing = await db.execute(
        select(EventAttending).where(
            EventAttending.event_id == event_id,
            EventAttending.user_id == payload.user_id,
        )
    )
    if existing.scalar_one_or_none():
        return SuccessResponse()
    attending = EventAttending(event_id=event_id, user_id=payload.user_id)
    db.add(attending)
    await db.flush()
    return SuccessResponse()


@router.delete("/events/{event_id}/likes", response_model=SuccessResponse)
async def remove_like(
    event_id: int = Path(..., description="Event ID"),
    user_id: int = Query(..., description="User whose like to remove"),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user's like from an event."""
    result = await db.execute(
        select(EventLike).where(EventLike.event_id == event_id, EventLike.user_id == user_id)
    )
    like = result.scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    await db.delete(like)
    await db.flush()
    return SuccessResponse()


@router.delete("/events/{event_id}/comments/{comment_id}", response_model=SuccessResponse)
async def remove_comment(
    event_id: int = Path(..., description="Event ID"),
    comment_id: int = Path(..., description="Comment ID to delete"),
    user_id: int = Query(..., description="User who owns the comment (must match)"),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user's comment from an event (comment must belong to the user)."""
    comment = await db.get(EventComment, comment_id)
    if not comment or comment.event_id != event_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot delete another user's comment")
    await db.delete(comment)
    await db.flush()
    return SuccessResponse()


@router.delete("/events/{event_id}/attending", response_model=SuccessResponse)
async def remove_attending(
    event_id: int = Path(..., description="Event ID"),
    user_id: int = Query(..., description="User whose attendance to remove"),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user's attendance from an event."""
    result = await db.execute(
        select(EventAttending).where(
            EventAttending.event_id == event_id,
            EventAttending.user_id == user_id,
        )
    )
    attending = result.scalar_one_or_none()
    if not attending:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    await db.delete(attending)
    await db.flush()
    return SuccessResponse()
