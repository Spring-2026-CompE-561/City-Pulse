"""Map city location strings to region IDs. Only 'san diego' supported (region_id 0)."""

REGION_SAN_DIEGO_ID = 0
VALID_REGION_STRINGS = ("san diego", "san-diego")


def city_location_to_region_id(city_location: str) -> int:
    """Convert city location string to region ID. Only 'san diego' is valid."""
    normalized = city_location.strip().lower().replace("-", " ")
    if normalized == "san diego":
        return REGION_SAN_DIEGO_ID
    raise ValueError(f"Unsupported city location. Only 'san diego' is allowed, got: {city_location!r}")


def region_id_to_city_location(region_id: int) -> str | None:
    """Convert region ID to city location string for display."""
    if region_id == REGION_SAN_DIEGO_ID:
        return "san diego"
    return None


def parse_region_param(value: str | int) -> int:
    """Accept region as string ('san diego', 'san-diego', '0') or int (0); return region_id."""
    if isinstance(value, int):
        if value == REGION_SAN_DIEGO_ID:
            return value
        raise ValueError(f"Unknown region id. Only {REGION_SAN_DIEGO_ID} (san diego) is supported.")
    s = value.strip().lower()
    if s == "0":
        return REGION_SAN_DIEGO_ID
    normalized = s.replace("-", " ")
    if normalized == "san diego":
        return REGION_SAN_DIEGO_ID
    raise ValueError(f"Unknown region. Only 'san diego' or '0' is supported, got: {value!r}")
