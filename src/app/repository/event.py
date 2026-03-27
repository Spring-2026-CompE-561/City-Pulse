"""Event repository compatibility module."""

from app.repositories.event_repository import (
    create_event,
    delete_event,
    delete_events_by_user_id,
    get_event_by_id,
    list_events_by_region,
    update_event_fields,
)

__all__ = [
    "list_events_by_region",
    "get_event_by_id",
    "create_event",
    "update_event_fields",
    "delete_event",
    "delete_events_by_user_id",
]

