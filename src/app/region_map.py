"""
Map city location strings to internal region IDs.

What lives here
- A tiny mapping layer between user-facing strings (e.g. "san diego") and DB `Region.id`.
- Parsing helpers used by request handlers (routers) to accept flexible query/path inputs.

Called by / import relationships
- `city_location_to_region_id` is used by:
  - `app.services.auth_service.register_user` (on registration)
  - `app.routers.users.update_user` (when updating city_location)
- `parse_region_param` is used by:
  - `app.routers.events.list_events`
  - `app.routers.regions.list_events_in_region` / `list_users_in_region`
  - `app.routers.trends.*`
  - `app.routers.interactions.list_events_with_interactions`
"""

# Region id constant used throughout the app and also seeded at startup in `app.database.init_db`.
REGION_SAN_DIEGO_ID = 0

# Input variants accepted for San Diego in some endpoints (informational; parsing uses normalization below).
VALID_REGION_STRINGS = ("san diego", "san-diego")


def city_location_to_region_id(city_location: str) -> int:
    """
    Convert a user-provided city location string to the internal region id.

    Called by
    - User creation/update flows to store `User.region_id` based on `city_location`.
    """
    # Normalize casing and separator differences (e.g. "San-Diego" -> "san diego").
    normalized = city_location.strip().lower().replace("-", " ")
    if normalized == "san diego":
        return REGION_SAN_DIEGO_ID
    raise ValueError(f"Unsupported city location. Only 'san diego' is allowed, got: {city_location!r}")


def region_id_to_city_location(region_id: int) -> str | None:
    """
    Convert an internal region id to a display string.

    Called by
    - `app.routers.users._user_to_read` and `app.services.auth_service.user_to_public`
      to show `city_location` in API responses.
    """
    if region_id == REGION_SAN_DIEGO_ID:
        return "san diego"
    return None


def parse_region_param(value: str | int) -> int:
    """
    Parse a region parameter from query/path inputs.

    Accepts
    - String: "san diego", "san-diego", or "0"
    - Int: 0

    Returns
    - The internal `region_id` to use in DB queries (currently only 0 supported).

    Called by
    - Routers that accept `region` as a query parameter or path segment.
    """
    if isinstance(value, int):
        if value == REGION_SAN_DIEGO_ID:
            return value
        raise ValueError(f"Unknown region id. Only {REGION_SAN_DIEGO_ID} (san diego) is supported.")
    # Normalize string input early for consistent comparisons.
    s = value.strip().lower()
    if s == "0":
        return REGION_SAN_DIEGO_ID
    normalized = s.replace("-", " ")
    if normalized == "san diego":
        return REGION_SAN_DIEGO_ID
    raise ValueError(f"Unknown region. Only 'san diego' or '0' is supported, got: {value!r}")
