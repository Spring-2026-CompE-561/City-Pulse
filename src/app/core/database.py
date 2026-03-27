"""Core database compatibility module."""

from app.database import async_session_maker, engine, get_db, init_db

__all__ = ["engine", "async_session_maker", "get_db", "init_db"]

