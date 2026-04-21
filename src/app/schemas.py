"""
Pydantic schemas for API request/response models.

What lives here
- Pure data models (no DB access) used to validate incoming request bodies and
  shape outgoing responses.

Called by / import relationships
- Routers import these classes and declare them as:
  - request bodies (e.g. `payload: UserCreate`)
  - response models (e.g. `response_model=UserRead`)
- Some routers return ORM models directly (e.g. Event), and `from_attributes=True`
  enables Pydantic to read ORM attributes into response schemas.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.event_categories import ALL_CATEGORIES_OPTION


# ----- User -----
class UserCreate(BaseModel):
    """Create user: name, email, password, city_location (only 'san diego' allowed)."""

    # Display name (required).
    name: str = Field(..., min_length=1, max_length=255)
    # Login identifier; normalized to lower-case in services/routers.
    email: str = Field(..., min_length=1, max_length=255)
    # Plain-text password provided by the client; hashed before storage (`app.auth.hash_password`).
    password: str = Field(..., min_length=1)
    # Human-friendly location string; mapped to `User.region_id` using `app.region_map.city_location_to_region_id`.
    city_location: str = Field(..., description="Only 'san diego' is supported.")


class UserUpdate(BaseModel):
    """Update user: current_password required; name, email, city_location optional."""

    # Required to authorize updates (verified via `app.auth.verify_password`).
    current_password: str = Field(..., min_length=1, description="Password to verify identity")
    # Optional changes.
    name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, min_length=1, max_length=255)
    city_location: str | None = Field(None, description="Only 'san diego' is supported.")


class UserDeleteBody(BaseModel):
    """Body for DELETE /api/users/{id}: password required to confirm deletion."""

    password: str = Field(..., min_length=1, description="Your current password to confirm account deletion.")


class UserRead(BaseModel):
    """User response: id, name, email, city_location (from region_id), created_at. Built in router, not from ORM."""

    # Public fields only (no password_hash).
    id: int
    name: str
    email: str
    city_location: str | None
    created_at: datetime


class UserListResponse(BaseModel):
    """Single object containing the user list and count. GET /api/users/ returns this."""

    # Returned by `app.routers.users.list_users`.
    users: list[UserRead]
    count: int


class LoginRequest(BaseModel):
    """Same as user identity: email and password only (no username)."""

    # Consumed by `app.routers.auth.login` -> `app.services.auth_service.login_user`.
    email: str = Field(..., min_length=1, description="Your email (same as when you created the account).")
    password: str = Field(..., min_length=1, description="Your current password.")


class RefreshRequest(BaseModel):
    """Body for POST /api/auth/refresh to get a new access token."""

    # Used by `app.routers.auth.refresh`.
    refresh_token: str = Field(..., min_length=1, description="Refresh token received from register or login.")


# ----- Region -----
class RegionRead(BaseModel):
    """Region: id and name (filing cabinet for events/users)."""

    # Allows building this schema from ORM objects (Region SQLModel instances).
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ----- Event (matches Event model: id, region_id, user_id, title, content, created_at) -----
class EventCreate(BaseModel):
    """Body for POST /api/events/: user_id, title, category, content. Region comes from user."""

    # Author user id; router validates that user exists and is in San Diego.
    user_id: int = Field(..., description="User posting the event (must have city_location = san diego).")
    title: str = Field(..., min_length=1, max_length=512)
    category: Literal[
        "Technology",
        "Arts & Culture",
        "Environment",
        "Entertainment",
        "Business",
        "Food & Drink",
        "Health & Wellness",
        "Music",
        "Nightlife",
        "Charity & Causes",
        "Community",
    ] = Field(..., description="Category selected from the frontend dropdown options.")
    content: str | None = Field(None, max_length=10000)
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    timezone: str = Field(default="America/Los_Angeles", max_length=100)
    venue_name: str | None = Field(None, max_length=255)
    venue_address: str | None = Field(None, max_length=512)
    neighborhood: str | None = Field(None, max_length=100)
    price_info: str | None = Field(None, max_length=255)


class EventUpdate(BaseModel):
    """Body for PUT /api/events/{id}: optional title/category/content."""

    # Partial update fields; router only updates provided values.
    title: str | None = Field(None, min_length=1, max_length=512)
    category: Literal[
        "Technology",
        "Arts & Culture",
        "Environment",
        "Entertainment",
        "Business",
        "Food & Drink",
        "Health & Wellness",
        "Music",
        "Nightlife",
        "Charity & Causes",
        "Community",
    ] | None = Field(None, description="Updated category from the frontend dropdown options.")
    content: str | None = None
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    timezone: str | None = Field(None, max_length=100)
    venue_name: str | None = Field(None, max_length=255)
    venue_address: str | None = Field(None, max_length=512)
    neighborhood: str | None = Field(None, max_length=100)
    price_info: str | None = Field(None, max_length=255)


class EventRead(BaseModel):
    """Response for GET /api/events/ and GET /api/events/{id}. Same fields as Event model."""

    # Allows building this schema from ORM objects (Event SQLModel instances).
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_id: int
    user_id: int | None
    title: str
    category: str
    content: str | None
    source_id: int | None = None
    source_name: str | None = None
    origin_type: str
    external_id: str | None = None
    external_url: str | None = None
    canonical_url: str | None = None
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    timezone: str
    venue_name: str | None = None
    venue_address: str | None = None
    neighborhood: str | None = None
    city: str
    price_info: str | None = None
    promo_summary: str | None = None
    tags_json: str | None = None
    source_confidence: float | None = None
    last_seen_at: datetime | None = None
    created_at: datetime


class EventCategoryOptionsResponse(BaseModel):
    """Allowed category values for frontend dropdown menus."""

    options: list[str] = Field(
        default_factory=lambda: [
            ALL_CATEGORIES_OPTION,
            "Technology",
            "Arts & Culture",
            "Environment",
            "Entertainment",
            "Business",
            "Food & Drink",
            "Health & Wellness",
            "Music",
            "Nightlife",
            "Charity & Causes",
            "Community",
        ]
    )


# ----- Trend (read-only for users; system maintains list) -----
class TrendEntryRead(BaseModel):
    """Single trend entry: event info plus rank and interaction counts."""

    event_id: int
    rank: int
    title: str
    attendance_count: int
    comments_count: int
    likes_count: int
    updated_at: datetime


class TrendRebuildBody(BaseModel):
    """Body for POST /api/trends: rebuild trend list for a region."""

    # Parsed using `app.region_map.parse_region_param`.
    region: str | int = Field("san diego", description="Region: 'san diego' or 0")


class TrendUpdateBody(BaseModel):
    """Body for PUT /api/trends: add/update one event in the trend list and reorder."""

    # `rank` is optional; the service/router will reorder by interaction stats either way.
    region: str | int = Field("san diego", description="Region: 'san diego' or 0")
    event_id: int = Field(..., description="Event to add or update in trends")
    rank: int | None = Field(None, ge=1, description="New rank (1-based). If omitted, event is appended or reordered by stats.")


# ----- Interactions -----
class CommentRead(BaseModel):
    """Single comment on an event."""

    id: int
    user_id: int
    event_id: int
    text: str
    created_at: datetime

    # Allows building this schema from ORM objects (EventComment SQLModel instances).
    model_config = ConfigDict(from_attributes=True)


class EventWithInteractionsRead(BaseModel):
    """Event with its interaction counts and recent comments."""

    id: int
    region_id: int
    user_id: int | None
    title: str
    category: str
    content: str | None
    source_id: int | None = None
    source_name: str | None = None
    origin_type: str
    external_url: str | None = None
    canonical_url: str | None = None
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    timezone: str
    venue_name: str | None = None
    venue_address: str | None = None
    neighborhood: str | None = None
    city: str
    price_info: str | None = None
    promo_summary: str | None = None
    source_confidence: float | None = None
    last_seen_at: datetime | None = None
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    attendance_count: int = 0
    comments: list[CommentRead] = Field(default_factory=list)

    # Allows model validation from ORM attributes (Event) plus extra computed fields.
    model_config = ConfigDict(from_attributes=True)


class InteractionLikeBody(BaseModel):
    """Deprecated body for PUT like; user identity comes from auth token."""


class InteractionCommentBody(BaseModel):
    """Body for PUT comment: authenticated user comments on an event."""

    text: str = Field(..., min_length=1, max_length=5000)


class InteractionAttendingBody(BaseModel):
    """Deprecated body for PUT attending; user identity comes from auth token."""


class InteractionRemoveBody(BaseModel):
    """Body for DELETE: remove user's like, comment, or attending."""

    user_id: int = Field(..., description="User whose interaction to remove")
    interaction_type: str = Field(..., description="One of: like, comment, attending")
    comment_id: int | None = Field(None, description="Required when interaction_type is 'comment' (the comment to delete)")


# ----- Common -----
class SuccessResponse(BaseModel):
    """Standard success for PUT/DELETE."""

    # Most endpoints return `{ "success": true }` for simple acknowledgements.
    success: bool = True


# ----- Ingestion / Source Management -----
class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_id: int
    name: str
    domain: str
    base_url: str
    source_type: str
    category_hint: str | None
    neighborhood: str | None
    is_active: bool
    crawl_allowed: bool
    crawl_delay_seconds: int
    rate_limit_per_min: int
    attribution_text: str | None
    robots_txt_url: str | None
    terms_url: str | None
    parse_strategy: str


class IngestRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_id: int
    source_id: int | None
    trigger_type: str
    status: str
    fetched_count: int
    inserted_count: int
    updated_count: int
    skipped_count: int
    error_count: int
    area: str | None
    error_summary: str | None
    started_at: datetime
    completed_at: datetime | None


class IngestRunRequest(BaseModel):
    source_id: int | None = Field(None, description="Optional source id. Omit to run all active sources.")
    area: str | None = Field(None, max_length=100, description="Neighborhood focus such as North Park.")
    start_date: datetime | None = None
    end_date: datetime | None = None


class PartnerSubmissionCreate(BaseModel):
    organizer_name: str = Field(..., min_length=1, max_length=255)
    organizer_contact: str | None = Field(None, max_length=255)
    instagram_handle: str | None = Field(None, max_length=255)
    instagram_post_url: str | None = Field(None, max_length=2048)
    external_event_url: str | None = Field(None, max_length=2048)
    title: str = Field(..., min_length=1, max_length=512)
    description: str | None = None
    category: Literal[
        "Technology",
        "Arts & Culture",
        "Environment",
        "Entertainment",
        "Business",
        "Food & Drink",
        "Health & Wellness",
        "Music",
        "Nightlife",
        "Charity & Causes",
        "Community",
    ] = "Arts & Culture"
    neighborhood: str | None = Field(None, max_length=100)
    venue_name: str | None = Field(None, max_length=255)
    venue_address: str | None = Field(None, max_length=512)
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None


class PartnerSubmissionReview(BaseModel):
    moderation_status: Literal["approved", "rejected"] = Field(
        ..., description="Review decision."
    )
    moderation_notes: str | None = None


class PartnerSubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_id: int
    submitted_by_user_id: int | None
    organizer_name: str
    organizer_contact: str | None
    instagram_handle: str | None
    instagram_post_url: str | None
    external_event_url: str | None
    title: str
    description: str | None
    category: str
    neighborhood: str | None
    venue_name: str | None
    venue_address: str | None
    event_start_at: datetime | None
    event_end_at: datetime | None
    moderation_status: str
    moderation_notes: str | None
    published_event_id: int | None
    created_at: datetime
    reviewed_at: datetime | None
