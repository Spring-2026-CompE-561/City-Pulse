"""Interactions API: list events with interactions; add/remove likes, comments, attending."""

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_required
from app.database import get_db
from app.exceptions import forbidden
from app.models import User
from app.region_map import parse_region_param
from app.repositories.event_repository import get_event_by_id, list_events_by_region
from app.repositories.interaction_repository import (
    add_attending as add_attending_row,
)
from app.repositories.interaction_repository import (
    add_comment as add_comment_row,
)
from app.repositories.interaction_repository import (
    add_like as add_like_row,
)
from app.repositories.interaction_repository import (
    get_attending,
    get_comment_by_id,
    get_event_interaction_counts,
    get_like,
    list_comments_for_event,
)
from app.repositories.interaction_repository import (
    remove_attending as remove_attending_row,
)
from app.repositories.interaction_repository import (
    remove_comment as remove_comment_row,
)
from app.repositories.interaction_repository import (
    remove_like as remove_like_row,
)
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
    events = await list_events_by_region(db, region_id=region_id, skip=skip, limit=limit)
    out = []
    for ev in events:
        if ev.id is None:
            continue
        event_id = ev.id
        likes_value, comments_value, attendance_value = await get_event_interaction_counts(
            db, event_id=event_id
        )
        comments = await list_comments_for_event(db, event_id=event_id)
        out.append(
            EventWithInteractionsRead(
                id=event_id,
                region_id=ev.region_id,
                user_id=ev.user_id,
                title=ev.title,
                content=ev.content,
                created_at=ev.created_at,
                likes_count=likes_value,
                comments_count=comments_value,
                attendance_count=attendance_value,
                comments=[CommentRead.model_validate(c) for c in comments],
            )
        )
    return out


@router.put("/events/{event_id}/likes", response_model=SuccessResponse)
async def add_like(
    event_id: int = Path(..., description="Event ID"),
    payload: InteractionLikeBody = Body(...),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Add a like from a user to an event (idempotent: already liked is success)."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    if payload.user_id != current_user.id:
        raise forbidden("Cannot add a like for another user")
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing = await get_like(db, event_id=event_id, user_id=payload.user_id)
    if existing:
        return SuccessResponse()
    await add_like_row(db, event_id=event_id, user_id=payload.user_id)
    return SuccessResponse()


@router.put("/events/{event_id}/comments", response_model=CommentRead, status_code=201)
async def add_comment(
    event_id: int = Path(..., description="Event ID"),
    payload: InteractionCommentBody = Body(...),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment from a user to an event."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    if payload.user_id != current_user.id:
        raise forbidden("Cannot add a comment for another user")
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    comment = await add_comment_row(
        db,
        event_id=event_id,
        user_id=payload.user_id,
        text=payload.text,
    )
    return comment


@router.put("/events/{event_id}/attending", response_model=SuccessResponse)
async def add_attending(
    event_id: int = Path(..., description="Event ID"),
    payload: InteractionAttendingBody = Body(...),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Add attendance: user marks they are attending the event (idempotent)."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    if payload.user_id != current_user.id:
        raise forbidden("Cannot add attendance for another user")
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    existing = await get_attending(db, event_id=event_id, user_id=payload.user_id)
    if existing:
        return SuccessResponse()
    await add_attending_row(db, event_id=event_id, user_id=payload.user_id)
    return SuccessResponse()


@router.delete("/events/{event_id}/likes", response_model=SuccessResponse)
async def remove_like(
    event_id: int = Path(..., description="Event ID"),
    user_id: int = Query(..., description="User whose like to remove"),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Remove a like from an event you own."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.user_id != current_user.id:
        raise forbidden("Cannot remove interactions from another user's event")
    like = await get_like(db, event_id=event_id, user_id=user_id)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    await remove_like_row(db, like=like)
    return SuccessResponse()


@router.delete("/events/{event_id}/comments/{comment_id}", response_model=SuccessResponse)
async def remove_comment(
    event_id: int = Path(..., description="Event ID"),
    comment_id: int = Path(..., description="Comment ID to delete"),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Remove a comment from an event you own."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.user_id != current_user.id:
        raise forbidden("Cannot remove interactions from another user's event")
    comment = await get_comment_by_id(db, comment_id=comment_id)
    if not comment or comment.event_id != event_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    await remove_comment_row(db, comment=comment)
    return SuccessResponse()


@router.delete("/events/{event_id}/attending", response_model=SuccessResponse)
async def remove_attending(
    event_id: int = Path(..., description="Event ID"),
    user_id: int = Query(..., description="User whose attendance to remove"),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Remove an attendance record from an event you own."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.user_id != current_user.id:
        raise forbidden("Cannot remove interactions from another user's event")
    attending = await get_attending(db, event_id=event_id, user_id=user_id)
    if not attending:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    await remove_attending_row(db, attending=attending)
    return SuccessResponse()
