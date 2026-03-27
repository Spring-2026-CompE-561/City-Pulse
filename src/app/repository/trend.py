"""Trend repository compatibility module."""

from app.repositories.trend_repository import (
    clear_region_trends,
    create_trend_row,
    flush,
    get_event_ids_in_region,
    get_event_interaction_counts_by_region,
    get_next_rank_for_region,
    get_trend_for_region_event,
    list_trends_for_region,
    list_trends_with_event_titles,
)

__all__ = [
    "list_trends_with_event_titles",
    "get_event_ids_in_region",
    "get_event_interaction_counts_by_region",
    "clear_region_trends",
    "create_trend_row",
    "get_trend_for_region_event",
    "get_next_rank_for_region",
    "list_trends_for_region",
    "flush",
]

