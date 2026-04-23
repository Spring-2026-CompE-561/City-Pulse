"""Event API: list events (default region san diego), create, update, delete."""

from datetime import datetime

from fastapi import APIRouter, Body, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_required
from app.database import get_db
from app.event_categories import (
    ALL_CATEGORIES_OPTION,
    ALLOWED_EVENT_CATEGORIES,
    parse_event_category_filter,
    validate_event_category,
)
from app.exceptions import bad_request, forbidden, not_found
from app.models import User
from app.region_map import REGION_SAN_DIEGO_ID, parse_region_param
from app.repository.event import (
    create_event as create_event_row,
)
from app.repository.event import (
    delete_event as delete_event_row,
)
from app.repository.event import (
    get_event_by_id,
    list_events_by_region,
    update_event_fields,
)
from app.schemas import (
    EventCategoryOptionsResponse,
    EventCreate,
    EventRead,
    EventUpdate,
    SuccessResponse,
)

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("/", response_model=list[EventRead])
async def list_events(
    region: str | int = Query("san diego", description="Region: 'san diego' or 0 (optional)"),
    category: str = Query(
        ALL_CATEGORIES_OPTION,
        description="Category filter. Use 'All Categories' to return every category.",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    neighborhood: str | None = Query(None, description="Optional neighborhood filter."),
    starts_after: datetime | None = Query(None, description="Filter events starting at/after this datetime."),
    starts_before: datetime | None = Query(None, description="Filter events starting at/before this datetime."),
    db: AsyncSession = Depends(get_db),
):
    """List events. Defaults to San Diego if no region given. Supports category filtering."""
    try:
        region_id = parse_region_param(region)
        category_filter = parse_event_category_filter(category)
    except ValueError as e:
        raise bad_request(str(e)) from e
    return await list_events_by_region(
        db,
        region_id=region_id,
        category=category_filter,
        neighborhood=neighborhood,
        starts_after=starts_after,
        starts_before=starts_before,
        skip=skip,
        limit=limit,
    )


@router.get("/categories", response_model=EventCategoryOptionsResponse)
async def list_categories():
    """Return allowed event categories for frontend dropdowns."""
    return EventCategoryOptionsResponse(options=[ALL_CATEGORIES_OPTION, *ALLOWED_EVENT_CATEGORIES])


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
async def create_event(
    payload: EventCreate,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Create a new event in the authenticated user's region."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    if payload.user_id != current_user.id:
        raise forbidden("Cannot create events for another user")

    user = current_user
    if user.region_id is None or user.region_id != REGION_SAN_DIEGO_ID:
        raise bad_request(
            "User must have city location 'san diego' to post events. Only San Diego is supported.",
        )
    # `User.id` is optional in the SQLModel type definitions, but it must be present
    # for a persisted user row (and for `events.user_id` to reference it).
    if user.id is None:
        raise RuntimeError("User id missing from database record")
    event = await create_event_row(
        db,
        region_id=user.region_id,
        user_id=user.id,
        title=payload.title,
        category=validate_event_category(payload.category),
        content=payload.content,
        event_start_at=payload.event_start_at,
        event_end_at=payload.event_end_at,
        timezone=payload.timezone,
        venue_name=payload.venue_name,
        venue_address=payload.venue_address,
        neighborhood=payload.neighborhood,
        price_info=payload.price_info,
    )
    return event


@router.put("/{id}", response_model=SuccessResponse)
async def update_event(
    id: int = Path(..., description="Event ID"),
    payload: EventUpdate = Body(...),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Update an event's title and/or content."""
    event = await get_event_by_id(db, id)
    if not event:
        raise not_found("Event not found")
    if event.user_id != current_user.id:
        raise forbidden("Cannot modify another user's event")
    try:
        normalized_category = (
            validate_event_category(payload.category) if payload.category is not None else None
        )
    except ValueError as e:
        raise bad_request(str(e)) from e
    await update_event_fields(
        db,
        event=event,
        title=payload.title,
        category=normalized_category,
        content=payload.content,
        event_start_at=payload.event_start_at,
        event_end_at=payload.event_end_at,
        timezone=payload.timezone,
        venue_name=payload.venue_name,
        venue_address=payload.venue_address,
        neighborhood=payload.neighborhood,
        price_info=payload.price_info,
    )
    return SuccessResponse()


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_event(
    id: int = Path(..., description="Event ID"),
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """Delete an event by ID."""
    event = await get_event_by_id(db, id)
    if not event:
        raise not_found("Event not found")
    if event.user_id != current_user.id:
        raise forbidden("Cannot delete another user's event")
    await delete_event_row(db, event=event)
    return SuccessResponse()

