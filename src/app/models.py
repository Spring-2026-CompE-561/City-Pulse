"""SQLAlchemy models: User, Region, Event, interactions (likes, comments, attending), Trend."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import text as sql_text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all models."""

    pass


class Region(Base):
    """
    Region model. Filing cabinet for events and users by location.
    Table: regions — id, name (e.g. San Diego). Only id=0 (san diego) for now.
    """

    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="region")
    users: Mapped[list["User"]] = relationship("User", back_populates="region")
    trends: Mapped[list["Trend"]] = relationship("Trend", back_populates="region", cascade="all, delete-orphan")


class User(Base):
    """
    User model. Includes city location (stored as region_id).
    Table: users — id, name, email, password_hash, created_at, region_id.
    First user gets id=0; then 1, 2, ... (id assigned in app, not autoincrement).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sql_text("CURRENT_TIMESTAMP")
    )
    region_id: Mapped[int | None] = mapped_column(
        ForeignKey("regions.id"), nullable=True, index=True
    )

    region: Mapped["Region | None"] = relationship("Region", back_populates="users")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="user")
    event_likes: Mapped[list["EventLike"]] = relationship("EventLike", back_populates="user", cascade="all, delete-orphan")
    event_comments: Mapped[list["EventComment"]] = relationship("EventComment", back_populates="user", cascade="all, delete-orphan")
    event_attending: Mapped[list["EventAttending"]] = relationship("EventAttending", back_populates="user", cascade="all, delete-orphan")


class Event(Base):
    """
    Event model. A post in a region (and optionally by a user).
    Table: events — id, region_id, user_id, title, content, created_at.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sql_text("CURRENT_TIMESTAMP")
    )

    region: Mapped["Region"] = relationship("Region", back_populates="events")
    user: Mapped["User | None"] = relationship("User", back_populates="events")
    likes: Mapped[list["EventLike"]] = relationship("EventLike", back_populates="event", cascade="all, delete-orphan")
    comments: Mapped[list["EventComment"]] = relationship("EventComment", back_populates="event", cascade="all, delete-orphan")
    attending: Mapped[list["EventAttending"]] = relationship("EventAttending", back_populates="event", cascade="all, delete-orphan")
    trend_entries: Mapped[list["Trend"]] = relationship("Trend", back_populates="event", cascade="all, delete-orphan")


class EventLike(Base):
    """User liked an event. One row per (user_id, event_id)."""

    __tablename__ = "event_likes"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_like_user_event"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="event_likes")
    event: Mapped["Event"] = relationship("Event", back_populates="likes")


class EventComment(Base):
    """User commented on an event."""

    __tablename__ = "event_comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sql_text("CURRENT_TIMESTAMP")
    )

    user: Mapped["User"] = relationship("User", back_populates="event_comments")
    event: Mapped["Event"] = relationship("Event", back_populates="comments")


class EventAttending(Base):
    """User is attending an event. One row per (user_id, event_id)."""

    __tablename__ = "event_attending"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_attending_user_event"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="event_attending")
    event: Mapped["Event"] = relationship("Event", back_populates="attending")


class Trend(Base):
    """Cached trend list per region: event_id, rank, and snapshot counts. Order: 1st attendance, 2nd comments, 3rd likes."""

    __tablename__ = "trends"
    __table_args__ = (UniqueConstraint("region_id", "event_id", name="uq_trend_region_event"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    attendance_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sql_text("CURRENT_TIMESTAMP")
    )

    region: Mapped["Region"] = relationship("Region", back_populates="trends")
    event: Mapped["Event"] = relationship("Event", back_populates="trend_entries")
