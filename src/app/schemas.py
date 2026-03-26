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

from pydantic import BaseModel, ConfigDict, Field


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
    """Body for POST /api/events/: user_id, title, content. Region comes from user."""

    # Author user id; router validates that user exists and is in San Diego.
    user_id: int = Field(..., description="User posting the event (must have city_location = san diego).")
    title: str = Field(..., min_length=1, max_length=512)
    content: str | None = Field(None, max_length=10000)


class EventUpdate(BaseModel):
    """Body for PUT /api/events/{id}: optional title and/or content."""

    # Partial update fields; router only updates provided values.
    title: str | None = Field(None, min_length=1, max_length=512)
    content: str | None = None


class EventRead(BaseModel):
    """Response for GET /api/events/ and GET /api/events/{id}. Same fields as Event model."""

    # Allows building this schema from ORM objects (Event SQLModel instances).
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_id: int
    user_id: int | None
    title: str
    content: str | None
    created_at: datetime


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
    content: str | None
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    attendance_count: int = 0
    comments: list[CommentRead] = Field(default_factory=list)

    # Allows model validation from ORM attributes (Event) plus extra computed fields.
    model_config = ConfigDict(from_attributes=True)


class InteractionLikeBody(BaseModel):
    """Body for PUT like: user adds a like to an event."""

    user_id: int = Field(..., description="User who is liking the event")


class InteractionCommentBody(BaseModel):
    """Body for PUT comment: user adds a comment to an event."""

    user_id: int = Field(..., description="User who is commenting")
    text: str = Field(..., min_length=1, max_length=5000)


class InteractionAttendingBody(BaseModel):
    """Body for PUT attending: user marks they are attending an event."""

    user_id: int = Field(..., description="User who is attending")


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
