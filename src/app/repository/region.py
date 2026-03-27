"""Region repository compatibility module."""

from app.repositories.region_repository import (
    list_events_in_region,
    list_regions,
    list_users_in_region,
    resolve_region_id_for_city_location,
)

__all__ = [
    "list_regions",
    "list_events_in_region",
    "list_users_in_region",
    "resolve_region_id_for_city_location",
]

