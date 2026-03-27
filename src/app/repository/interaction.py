"""Interaction repository compatibility module."""

from app.repositories.interaction_repository import (
    add_attending,
    add_comment,
    add_like,
    get_attending,
    get_comment_by_id,
    get_counts_for_event_ids,
    get_event_interaction_counts,
    get_like,
    list_comments_for_event,
    remove_attending,
    remove_comment,
    remove_like,
)

__all__ = [
    "get_like",
    "add_like",
    "remove_like",
    "add_comment",
    "get_comment_by_id",
    "list_comments_for_event",
    "remove_comment",
    "get_attending",
    "add_attending",
    "remove_attending",
    "get_event_interaction_counts",
    "get_counts_for_event_ids",
]

