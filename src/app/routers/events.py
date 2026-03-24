"""Event API: list events (default region san diego), create, update, delete."""

from fastapi import APIRouter, Body, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import bad_request, not_found
from app.database import get_db
from app.models import User
from app.repositories.event_repository import (
    create_event as create_event_row,
    delete_event as delete_event_row,
    get_event_by_id,
    list_events_by_region,
    update_event_fields,
)
from app.region_map import REGION_SAN_DIEGO_ID, parse_region_param
from app.schemas import EventCreate, EventRead, EventUpdate, SuccessResponse

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("/", response_model=list[EventRead])
async def list_events(
    region: str | int = Query("san diego", description="Region: 'san diego' or 0 (optional)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List events. Defaults to San Diego if no region given. Matches Event model: id, region_id, user_id, title, content, created_at."""
    try:
        region_id = parse_region_param(region)
    except ValueError as e:
        raise bad_request(str(e)) from e
    return await list_events_by_region(db, region_id=region_id, skip=skip, limit=limit)


@router.get("/{id}", response_model=EventRead)
async def get_event(
    id: int = Path(..., description="Event ID (the 'id' field from the event list)"),
    db: AsyncSession = Depends(get_db),
):
    """Get one event by ID. Response matches Event model."""
    event = await get_event_by_id(db, id)
    if not event:
        raise not_found("Event not found")
    return event


@router.post("/", response_model=EventRead, status_code=201)
async def create_event(payload: EventCreate, db: AsyncSession = Depends(get_db)):
    """Create a new event in the user's region. User must have city_location = san diego."""
    user = await db.get(User, payload.user_id)
    if not user:
        raise not_found("User not found")
    if user.region_id is None or user.region_id != REGION_SAN_DIEGO_ID:
        raise bad_request(
            "User must have city location 'san diego' to post events. Only San Diego is supported.",
        )
    event = await create_event_row(
        db,
        region_id=user.region_id,
        user_id=user.id,
        title=payload.title,
        content=payload.content,
    )
    return event


@router.put("/{id}", response_model=SuccessResponse)
async def update_event(
    id: int = Path(..., description="Event ID"),
    payload: EventUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Update an event's title and/or content."""
    event = await get_event_by_id(db, id)
    if not event:
        raise not_found("Event not found")
    await update_event_fields(db, event=event, title=payload.title, content=payload.content)
    return SuccessResponse()


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_event(
    id: int = Path(..., description="Event ID"),
    db: AsyncSession = Depends(get_db),
):
    """Delete an event by ID."""
    event = await get_event_by_id(db, id)
    if not event:
        raise not_found("Event not found")
    await delete_event_row(db, event=event)
    return SuccessResponse()
