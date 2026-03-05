"""SQLModel models: User, Region, Event, interactions (likes, comments, attending), Trend."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel


class Region(SQLModel, table=True):
    """
    Region model. Filing cabinet for events and users by location.
    Table: regions — id, name (e.g. San Diego). Only id=0 (san diego) for now.
    """

    __tablename__ = "regions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, max_length=255)

    events: list["Event"] = Relationship(back_populates="region")
    users: list["User"] = Relationship(back_populates="region")
    trends: list["Trend"] = Relationship(back_populates="region")


class User(SQLModel, table=True):
    """
    User model. Includes city location (stored as region_id).
    Table: users — id, name, email, password_hash, created_at, region_id.
    First user gets id=0; then 1, 2, ... (id assigned in app).
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, max_length=255)
    email: str = Field(nullable=False, max_length=255, index=True)
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    region_id: Optional[int] = Field(default=None, foreign_key="regions.id", index=True)

    region: Optional[Region] = Relationship(back_populates="users")
    events: list["Event"] = Relationship(back_populates="user")
    event_likes: list["EventLike"] = Relationship(back_populates="user")
    event_comments: list["EventComment"] = Relationship(back_populates="user")
    event_attending: list["EventAttending"] = Relationship(back_populates="user")


class Event(SQLModel, table=True):
    """
    Event model. A post in a region (and optionally by a user).
    Table: events — id, region_id, user_id, title, content, created_at.
    """

    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_id: int = Field(foreign_key="regions.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    title: str = Field(nullable=False, max_length=512)
    content: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    region: Region = Relationship(back_populates="events")
    user: Optional[User] = Relationship(back_populates="events")
    likes: list["EventLike"] = Relationship(back_populates="event")
    comments: list["EventComment"] = Relationship(back_populates="event")
    attending: list["EventAttending"] = Relationship(back_populates="event")
    trend_entries: list["Trend"] = Relationship(back_populates="event")


class EventLike(SQLModel, table=True):
    """User liked an event. One row per (user_id, event_id)."""

    __tablename__ = "event_likes"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_like_user_event"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    event_id: int = Field(foreign_key="events.id", index=True)

    user: User = Relationship(back_populates="event_likes")
    event: Event = Relationship(back_populates="likes")


class EventComment(SQLModel, table=True):
    """User commented on an event."""

    __tablename__ = "event_comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    text: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    user: User = Relationship(back_populates="event_comments")
    event: Event = Relationship(back_populates="comments")


class EventAttending(SQLModel, table=True):
    """User is attending an event. One row per (user_id, event_id)."""

    __tablename__ = "event_attending"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_attending_user_event"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    event_id: int = Field(foreign_key="events.id", index=True)

    user: User = Relationship(back_populates="event_attending")
    event: Event = Relationship(back_populates="attending")


class Trend(SQLModel, table=True):
    """Cached trend list per region: event_id, rank, and snapshot counts. Order: 1st attendance, 2nd comments, 3rd likes."""

    __tablename__ = "trends"
    __table_args__ = (UniqueConstraint("region_id", "event_id", name="uq_trend_region_event"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    region_id: int = Field(foreign_key="regions.id", index=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    rank: int
    attendance_count: int = 0
    comments_count: int = 0
    likes_count: int = 0
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    region: Region = Relationship(back_populates="trends")
    event: Event = Relationship(back_populates="trend_entries")
