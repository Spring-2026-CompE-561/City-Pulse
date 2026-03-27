"""User repository compatibility module."""

from app.repositories.user_repository import (
    create_user,
    delete_user_and_events,
    get_next_user_id,
    get_user_by_email,
    get_user_by_id,
    list_users,
)

__all__ = [
    "get_next_user_id",
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "list_users",
    "delete_user_and_events",
]

