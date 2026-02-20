"""Pydantic schemas for API request/response."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ----- User -----
class UserCreate(BaseModel):
    """Create user: name, email, password, city_location (only 'san diego' allowed)."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)
    city_location: str = Field(..., description="Only 'san diego' is supported.")


class UserUpdate(BaseModel):
    """Update user: current_password required; name, email, city_location optional."""

    current_password: str = Field(..., min_length=1, description="Password to verify identity")
    name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, min_length=1, max_length=255)
    city_location: str | None = Field(None, description="Only 'san diego' is supported.")


class UserRead(BaseModel):
    """User response: id, name, email, city_location (from region_id), created_at. Built in router, not from ORM."""

    id: int
    name: str
    email: str
    city_location: str | None
    created_at: datetime


class UserListResponse(BaseModel):
    """Single object containing the user list and count. GET /api/users/ returns this."""

    users: list[UserRead]
    count: int


class LoginRequest(BaseModel):
    """Same as user identity: email and password only (no username)."""

    email: str = Field(..., min_length=1, description="Your email (same as when you created the account).")
    password: str = Field(..., min_length=1, description="Your current password.")


# ----- Region -----
class RegionRead(BaseModel):
    """Region: id and name (filing cabinet for events/users)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ----- Event (matches Event model: id, region_id, user_id, title, content, created_at) -----
class EventCreate(BaseModel):
    """Body for POST /api/events/: user_id, title, content. Region comes from user."""

    user_id: int = Field(..., description="User posting the event (must have city_location = san diego).")
    title: str = Field(..., min_length=1, max_length=512)
    content: str | None = Field(None, max_length=10000)


class EventUpdate(BaseModel):
    """Body for PUT /api/events/{id}: optional title and/or content."""

    title: str | None = Field(None, min_length=1, max_length=512)
    content: str | None = None


class EventRead(BaseModel):
    """Response for GET /api/events/ and GET /api/events/{id}. Same fields as Event model."""

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

    region: str | int = Field("san diego", description="Region: 'san diego' or 0")


class TrendUpdateBody(BaseModel):
    """Body for PUT /api/trends: add/update one event in the trend list and reorder."""

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

    success: bool = True
