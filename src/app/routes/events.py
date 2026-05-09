"""Event API: list events (default region san diego), create, update, delete."""

from datetime import UTC, datetime, timedelta, tzinfo
import json
from pathlib import Path as FilePath
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, File, Path, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_required
from app.database import get_db
from app.event_metadata import clean_event_description, clean_organizer_name, extract_organizer_name
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
    delete_past_events_older_than,
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
    EventImageUploadResponse,
    EventRead,
    EventUpdate,
    SuccessResponse,
)

router = APIRouter(prefix="/api/events", tags=["Events"])
EVENT_MEDIA_DIR = FilePath(__file__).resolve().parents[2] / "media" / "events"
ALLOWED_EVENT_MEDIA_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "application/pdf": ".pdf",
}
MAX_EVENT_MEDIA_BYTES = 10 * 1024 * 1024
PAST_EVENT_RETENTION_DAYS = 7


def resolve_feed_timezone() -> tzinfo:
    try:
        return ZoneInfo("America/Los_Angeles")
    except ZoneInfoNotFoundError:
        return UTC


FEED_TIMEZONE = resolve_feed_timezone()


def current_feed_time() -> datetime:
    """Return current local feed time used for active event filtering."""
    return datetime.now(FEED_TIMEZONE)


@router.get("", response_model=list[EventRead], include_in_schema=False)
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
    now_local = current_feed_time()
    retention_cutoff = now_local - timedelta(days=PAST_EVENT_RETENTION_DAYS)
    await delete_past_events_older_than(
        db,
        region_id=region_id,
        retention_cutoff=retention_cutoff,
    )
    return await list_events_by_region(
        db,
        region_id=region_id,
        category=category_filter,
        neighborhood=neighborhood,
        starts_after=starts_after,
        starts_before=starts_before,
        active_after=now_local,
        skip=skip,
        limit=limit,
    )


@router.get("/categories", response_model=EventCategoryOptionsResponse)
async def list_categories():
    """Return allowed event categories for frontend dropdowns."""
    return EventCategoryOptionsResponse(options=[ALL_CATEGORIES_OPTION, *ALLOWED_EVENT_CATEGORIES])


@router.post("/upload-image", response_model=EventImageUploadResponse)
async def upload_event_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_required),
):
    """Upload an event media file (JPEG/PNG/PDF) and return a public media URL."""
    if current_user.id is None:
        raise RuntimeError("User id missing from database record")
    if file.content_type not in ALLOWED_EVENT_MEDIA_TYPES:
        raise bad_request("Only JPEG, PNG, and PDF files are allowed")
    file_bytes = await file.read()
    if not file_bytes:
        raise bad_request("Uploaded file is empty")
    if len(file_bytes) > MAX_EVENT_MEDIA_BYTES:
        raise bad_request("File too large (max 10 MB)")

    EVENT_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    extension = ALLOWED_EVENT_MEDIA_TYPES[file.content_type]
    generated_name = f"{uuid4().hex}{extension}"
    target_path = EVENT_MEDIA_DIR / generated_name
    target_path.write_bytes(file_bytes)
    return EventImageUploadResponse(url=f"/media/events/{generated_name}")


@router.get("/{id}", response_model=EventRead)
async def get_event(
    id: int = Path(..., description="Event ID (the 'id' field from the event list)"),
    db: AsyncSession = Depends(get_db),
):
    """Get one event by ID. Response matches Event model."""
    event = await get_event_by_id(db, id)
    if not event:
        raise not_found("Event not found")
    organizer_name = (
        extract_organizer_name(event.tags_json)
        or (event.user.name if event.user is not None else None)
        or event.venue_name
        or (event.source.name if event.source else None)
    )
    content = clean_event_description(
        event.content,
        title=event.title,
        venue_name=event.venue_name,
    )
    return EventRead(
        id=event.id,
        region_id=event.region_id,
        user_id=event.user_id,
        user_name=event.user.name if event.user else None,
        title=event.title,
        category=event.category,
        content=content,
        source_id=event.source_id,
        source_name=event.source.name if event.source else None,
        organizer_name=organizer_name,
        origin_type=event.origin_type,
        external_id=event.external_id,
        external_url=event.external_url,
        canonical_url=event.canonical_url,
        event_image_url=event.event_image_url,
        event_start_at=event.event_start_at,
        event_end_at=event.event_end_at,
        timezone=event.timezone,
        venue_name=event.venue_name,
        venue_address=event.venue_address,
        neighborhood=event.neighborhood,
        city=event.city,
        price_info=event.price_info,
        promo_summary=event.promo_summary,
        tags_json=event.tags_json,
        source_confidence=event.source_confidence,
        last_seen_at=event.last_seen_at,
        created_at=event.created_at,
    )


@router.post("", response_model=EventRead, status_code=201, include_in_schema=False)
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
    normalized_organizer_name = clean_organizer_name(payload.organizer_name)
    event = await create_event_row(
        db,
        region_id=user.region_id,
        user_id=user.id,
        title=payload.title,
        category=validate_event_category(payload.category),
        content=payload.content,
        event_image_url=payload.event_image_url,
        event_start_at=payload.event_start_at,
        event_end_at=payload.event_end_at,
        timezone=payload.timezone,
        venue_name=payload.venue_name,
        venue_address=payload.venue_address,
        neighborhood=payload.neighborhood,
        price_info=payload.price_info,
        tags_json=(
            json.dumps({"organizer_name": normalized_organizer_name})
            if normalized_organizer_name is not None
            else None
        ),
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
        event_image_url=payload.event_image_url,
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

