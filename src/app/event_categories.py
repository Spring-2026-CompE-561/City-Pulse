"""Allowed event categories and validation helpers."""

ALLOWED_EVENT_CATEGORIES: tuple[str, ...] = (
    "Music",
    "Arts & Culture",
    "Food & Drink",
    "Entertainment",
    "Nightlife (Bars & Clubs)",
)

ALL_CATEGORIES_OPTION = "All Categories"


LEGACY_CATEGORY_ALIASES: dict[str, str] = {
    "Technology": "Entertainment",
    "Environment": "Arts & Culture",
    "Business": "Entertainment",
    "Health & Wellness": "Arts & Culture",
    "Nightlife": "Nightlife (Bars & Clubs)",
    "Charity & Causes": "Arts & Culture",
    "Community": "Entertainment",
}


def normalize_event_category(category: str) -> str:
    """Normalize legacy category values to the current labels."""
    value = category.strip()
    if not value:
        return value
    return LEGACY_CATEGORY_ALIASES.get(value, value)


def validate_event_category(category: str) -> str:
    """
    Return a normalized event category if valid, else raise ValueError.
    """
    value = normalize_event_category(category)
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
    value = normalize_event_category(category)
    if not value or value == ALL_CATEGORIES_OPTION:
        return None
    return validate_event_category(value)

