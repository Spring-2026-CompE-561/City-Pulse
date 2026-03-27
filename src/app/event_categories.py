"""Allowed event categories and validation helpers."""

ALLOWED_EVENT_CATEGORIES: tuple[str, ...] = (
    "Technology",
    "Arts & Culture",
    "Environment",
    "Entertainment",
    "Business",
    "Food & Drink",
    "Health & Wellness",
    "Music",
)

ALL_CATEGORIES_OPTION = "All Categories"


def validate_event_category(category: str) -> str:
    """
    Return a normalized event category if valid, else raise ValueError.
    """
    value = category.strip()
    if value not in ALLOWED_EVENT_CATEGORIES:
        raise ValueError(
            "Invalid category. Allowed values: "
            + ", ".join(ALLOWED_EVENT_CATEGORIES)
        )
    return value


def parse_event_category_filter(category: str | None) -> str | None:
    """
    Parse list filter category.

    - None or 'All Categories' means no category filter.
    - Any other value must be a valid event category.
    """
    if category is None:
        return None
    value = category.strip()
    if not value or value == ALL_CATEGORIES_OPTION:
        return None
    return validate_event_category(value)

