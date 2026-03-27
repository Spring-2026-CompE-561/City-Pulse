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
    # Server-side creation timestamp.
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # ORM relationships.
    region: Region = Relationship(back_populates="events")
    user: User | None = Relationship(back_populates="events")
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
