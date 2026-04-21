"""
SQLModel ORM models for City Pulse.

What lives here
- Database table models (`SQLModel, table=True`) that define schema + relationships.
- These classes are used in:
  - Routers for queries/CRUD
  - Services/repositories for business logic and persistence
  - `app.database.init_db()` via `SQLModel.metadata.create_all` (requires models imported at startup)

Called by / import relationships
- Imported in `app.main` (as `from app import models`) to ensure metadata is registered before table creation.
- Imported throughout routers/services/repositories for querying (`select(Model)`) and inserts (`db.add(...)`).
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel


class Region(SQLModel, table=True):
    """
    Region model. Filing cabinet for events and users by location.
    Table: regions — id, name (e.g. San Diego). Only id=0 (san diego) for now.
    """

    __tablename__ = "regions"  # pyright: ignore[reportAssignmentType]

    # Primary key. In this project, region id 0 is reserved for San Diego (see `app.region_map`).
    id: int | None = Field(default=None, primary_key=True)
    # Display name. Indexed for fast lookups by name if needed.
    name: str = Field(index=True, nullable=False, max_length=255)

    # Relationship collections:
    # - Used by SQLModel/SQLAlchemy for eager/lazy navigation (not directly exposed by routers here).
    events: list["Event"] = Relationship(back_populates="region")
    users: list["User"] = Relationship(back_populates="region")
    trends: list["Trend"] = Relationship(back_populates="region")
    sources: list["Source"] = Relationship(back_populates="region")
    partner_submissions: list["PartnerSubmission"] = Relationship(back_populates="region")


class User(SQLModel, table=True):
    """
    User model. Includes city location (stored as region_id).
    Table: users — id, name, email, password_hash, created_at, region_id.
    First user gets id=0; then 1, 2, ... (id assigned in app).
    """

    __tablename__ = "users"  # pyright: ignore[reportAssignmentType]

    # Primary key. This app assigns user ids manually (see `app.repositories.user_repository.get_next_user_id`).
    id: int | None = Field(default=None, primary_key=True)
    # User display name.
    name: str = Field(nullable=False, max_length=255)
    # Email is indexed for login lookups (`get_user_by_email`).
    email: str = Field(nullable=False, max_length=255, index=True)
    # Stored password hash (SHA-256 in `app.auth`).
    password_hash: str = Field(nullable=False, max_length=255)
    # Server-side creation timestamp (set by DB default).
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    # Foreign key to `regions.id`. This is the stored version of "city_location".
    region_id: int | None = Field(default=None, foreign_key="regions.id", index=True)

    # ORM relationships for navigation.
    region: Region | None = Relationship(back_populates="users")
    events: list["Event"] = Relationship(back_populates="user")
    event_likes: list["EventLike"] = Relationship(back_populates="user")
    event_comments: list["EventComment"] = Relationship(back_populates="user")
    event_attending: list["EventAttending"] = Relationship(back_populates="user")


class Event(SQLModel, table=True):
    """
    Event model. A post in a region (and optionally by a user).
    Table: events — id, region_id, user_id, title, category, content, created_at.
    """

    __tablename__ = "events"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_event_source_external"),
        UniqueConstraint("canonical_url", name="uq_event_canonical_url"),
    )

    # Primary key.
    id: int | None = Field(default=None, primary_key=True)
    # Region this event belongs to (San Diego only currently).
    region_id: int = Field(foreign_key="regions.id", index=True)
    # Optional author user id (events are created with a user in `app.routers.events.create_event`).
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    # Title is required and bounded in length by schema.
    title: str = Field(nullable=False, max_length=512)
    # Category is required and validated in `app.event_categories`.
    category: str = Field(default="Technology", nullable=False, max_length=100, index=True)
    # Optional body/content.
    content: str | None = Field(default=None)
    # Optional imported-source information.
    source_id: int | None = Field(default=None, foreign_key="sources.id", index=True)
    origin_type: str = Field(default="user", nullable=False, max_length=20, index=True)
    external_id: str | None = Field(default=None, max_length=255)
    external_url: str | None = Field(default=None, max_length=2048)
    canonical_url: str | None = Field(default=None, max_length=2048)
    # Event timing and location metadata.
    event_start_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )
    event_end_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    timezone: str = Field(default="America/Los_Angeles", nullable=False, max_length=100)
    venue_name: str | None = Field(default=None, max_length=255)
    venue_address: str | None = Field(default=None, max_length=512)
    neighborhood: str | None = Field(default=None, max_length=100, index=True)
    city: str = Field(default="San Diego", nullable=False, max_length=100, index=True)
    price_info: str | None = Field(default=None, max_length=255)
    promo_summary: str | None = Field(default=None, max_length=1024)
    tags_json: str | None = Field(default=None)
    source_confidence: float | None = Field(default=None)
    last_seen_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    # Server-side creation timestamp.
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # ORM relationships.
    region: Region = Relationship(back_populates="events")
    user: User | None = Relationship(back_populates="events")
    source: "Source" | None = Relationship(back_populates="events")
    likes: list["EventLike"] = Relationship(back_populates="event")
    comments: list["EventComment"] = Relationship(back_populates="event")
    attending: list["EventAttending"] = Relationship(back_populates="event")
    trend_entries: list["Trend"] = Relationship(back_populates="event")


class EventLike(SQLModel, table=True):
    """User liked an event. One row per (user_id, event_id)."""

    __tablename__ = "event_likes"  # pyright: ignore[reportAssignmentType]
    # Enforce idempotency at the DB level: one like per (user, event).
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_like_user_event"),)

    id: int | None = Field(default=None, primary_key=True)
    # User who liked.
    user_id: int = Field(foreign_key="users.id", index=True)
    # Event that was liked.
    event_id: int = Field(foreign_key="events.id", index=True)

    user: User = Relationship(back_populates="event_likes")
    event: Event = Relationship(back_populates="likes")


class EventComment(SQLModel, table=True):
    """User commented on an event."""

    __tablename__ = "event_comments"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    # Author of the comment.
    user_id: int = Field(foreign_key="users.id", index=True)
    # Event being commented on.
    event_id: int = Field(foreign_key="events.id", index=True)
    # Comment text/body.
    text: str = Field(nullable=False)
    # Server-side creation timestamp.
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    user: User = Relationship(back_populates="event_comments")
    event: Event = Relationship(back_populates="comments")


class EventAttending(SQLModel, table=True):
    """User is attending an event. One row per (user_id, event_id)."""

    __tablename__ = "event_attending"  # pyright: ignore[reportAssignmentType]
    # Enforce idempotency at the DB level: one attendance record per (user, event).
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_attending_user_event"),)

    id: int | None = Field(default=None, primary_key=True)
    # User attending.
    user_id: int = Field(foreign_key="users.id", index=True)
    # Event attended.
    event_id: int = Field(foreign_key="events.id", index=True)

    user: User = Relationship(back_populates="event_attending")
    event: Event = Relationship(back_populates="attending")


class Trend(SQLModel, table=True):
    """Cached trend list per region: event_id, rank, and snapshot counts. Order: 1st attendance, 2nd comments, 3rd likes."""

    __tablename__ = "trends"  # pyright: ignore[reportAssignmentType]
    # Ensure an event appears at most once in a region's trend list.
    __table_args__ = (UniqueConstraint("region_id", "event_id", name="uq_trend_region_event"),)

    id: int | None = Field(default=None, primary_key=True)
    # Region the trend snapshot applies to.
    region_id: int = Field(foreign_key="regions.id", index=True)
    # Event being ranked.
    event_id: int = Field(foreign_key="events.id", index=True)
    # 1-based rank (lower is "more trending").
    rank: int
    # Snapshot interaction counts at the time of rebuild/update.
    attendance_count: int = 0
    comments_count: int = 0
    likes_count: int = 0
    # Server-side timestamp (DB default).
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    region: Region = Relationship(back_populates="trends")
    event: Event = Relationship(back_populates="trend_entries")


class Source(SQLModel, table=True):
    """External source registry for ingestion connectors."""

    __tablename__ = "sources"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (UniqueConstraint("name", "region_id", name="uq_source_name_region"),)

    id: int | None = Field(default=None, primary_key=True)
    region_id: int = Field(foreign_key="regions.id", index=True)
    name: str = Field(nullable=False, max_length=255)
    domain: str = Field(nullable=False, max_length=255, index=True)
    base_url: str = Field(nullable=False, max_length=2048)
    source_type: str = Field(default="html", nullable=False, max_length=50, index=True)
    category_hint: str | None = Field(default=None, max_length=100)
    neighborhood: str | None = Field(default=None, max_length=100, index=True)
    is_active: bool = Field(default=True, nullable=False, index=True)
    crawl_allowed: bool = Field(default=False, nullable=False)
    crawl_delay_seconds: int = Field(default=10, nullable=False)
    rate_limit_per_min: int = Field(default=10, nullable=False)
    attribution_text: str | None = Field(default=None, max_length=512)
    robots_txt_url: str | None = Field(default=None, max_length=2048)
    terms_url: str | None = Field(default=None, max_length=2048)
    parse_strategy: str = Field(default="generic_html", nullable=False, max_length=100)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    region: Region = Relationship(back_populates="sources")
    events: list[Event] = Relationship(back_populates="source")


class IngestRun(SQLModel, table=True):
    """Execution log for each ingestion run."""

    __tablename__ = "ingest_runs"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    region_id: int = Field(foreign_key="regions.id", index=True)
    source_id: int | None = Field(default=None, foreign_key="sources.id", index=True)
    trigger_type: str = Field(default="manual", nullable=False, max_length=50)
    status: str = Field(default="running", nullable=False, max_length=50, index=True)
    fetched_count: int = Field(default=0, nullable=False)
    inserted_count: int = Field(default=0, nullable=False)
    updated_count: int = Field(default=0, nullable=False)
    skipped_count: int = Field(default=0, nullable=False)
    error_count: int = Field(default=0, nullable=False)
    area: str | None = Field(default=None, max_length=100)
    error_summary: str | None = Field(default=None)
    started_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class PartnerSubmission(SQLModel, table=True):
    """Manual/official submissions for Instagram-compatible intake."""

    __tablename__ = "partner_submissions"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    region_id: int = Field(foreign_key="regions.id", index=True)
    submitted_by_user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    organizer_name: str = Field(nullable=False, max_length=255)
    organizer_contact: str | None = Field(default=None, max_length=255)
    instagram_handle: str | None = Field(default=None, max_length=255)
    instagram_post_url: str | None = Field(default=None, max_length=2048)
    external_event_url: str | None = Field(default=None, max_length=2048)
    title: str = Field(nullable=False, max_length=512)
    description: str | None = Field(default=None)
    category: str = Field(default="Arts & Culture", nullable=False, max_length=100)
    neighborhood: str | None = Field(default=None, max_length=100)
    venue_name: str | None = Field(default=None, max_length=255)
    venue_address: str | None = Field(default=None, max_length=512)
    event_start_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    event_end_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    moderation_status: str = Field(default="pending", nullable=False, max_length=50, index=True)
    moderation_notes: str | None = Field(default=None)
    published_event_id: int | None = Field(default=None, foreign_key="events.id", index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    reviewed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    region: Region = Relationship(back_populates="partner_submissions")
