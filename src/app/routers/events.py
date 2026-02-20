"""Event API: list events (default region san diego), create, update, delete."""

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Event, User
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
        raise HTTPException(status_code=400, detail=str(e)) from e
    result = await db.execute(
        select(Event).where(Event.region_id == region_id).offset(skip).limit(limit)
    )
    events = list(result.scalars().all())
    return events


@router.get("/{id}", response_model=EventRead)
async def get_event(
    id: int = Path(..., description="Event ID (the 'id' field from the event list)"),
    db: AsyncSession = Depends(get_db),
):
    """Get one event by ID. Response matches Event model."""
    event = await db.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventRead, status_code=201)
async def create_event(payload: EventCreate, db: AsyncSession = Depends(get_db)):
    """Create a new event in the user's region. User must have city_location = san diego."""
    user = await db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.region_id is None or user.region_id != REGION_SAN_DIEGO_ID:
        raise HTTPException(
            status_code=400,
            detail="User must have city location 'san diego' to post events. Only San Diego is supported.",
        )
    event = Event(
        region_id=user.region_id,
        user_id=user.id,
        title=payload.title,
        content=payload.content,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


@router.put("/{id}", response_model=SuccessResponse)
async def update_event(
    id: int = Path(..., description="Event ID"),
    payload: EventUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Update an event's title and/or content."""
    event = await db.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if payload.title is not None:
        event.title = payload.title
    if payload.content is not None:
        event.content = payload.content
    await db.flush()
    return SuccessResponse()


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_event(
    id: int = Path(..., description="Event ID"),
    db: AsyncSession = Depends(get_db),
):
    """Delete an event by ID."""
    event = await db.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(event)
    await db.flush()
    return SuccessResponse()
