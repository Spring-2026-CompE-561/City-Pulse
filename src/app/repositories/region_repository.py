from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import Event, Region, User
from app.region_map import city_location_to_region_id


async def list_regions(db: AsyncSession) -> list[Region]:
    result = await db.execute(select(Region).order_by(col(Region.id)))
    return list(result.scalars().all())


async def list_events_in_region(db: AsyncSession, *, region_id: int) -> list[Event]:
    result = await db.execute(select(Event).where(col(Event.region_id) == region_id))
    return list(result.scalars().all())


async def list_users_in_region(db: AsyncSession, *, region_id: int) -> list[User]:
    result = await db.execute(select(User).where(col(User.region_id) == region_id))
    return list(result.scalars().all())


async def resolve_region_id_for_city_location(
    db: AsyncSession, *, city_location: str
) -> int:
    """
    Resolve city_location to an existing Region.id.

    Prefers the canonical mapped id (currently 0), but falls back to the first
    region row that matches by normalized name to keep older databases working.
    """
    preferred_region_id = city_location_to_region_id(city_location)
    preferred = await db.get(Region, preferred_region_id)
    if preferred is not None:
        return preferred_region_id

    normalized_name = city_location.strip().lower().replace("-", " ")
    result = await db.execute(
        select(col(Region.id))
        .where(func.lower(col(Region.name)) == normalized_name)
        .order_by(col(Region.id))
        .limit(1)
    )
    region_id = result.scalar_one_or_none()
    if region_id is None:
        raise ValueError(
            f"Unsupported city location. Only 'san diego' is allowed, got: {city_location!r}"
        )
    return region_id
