from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import Event, Region, User


async def list_regions(db: AsyncSession) -> list[Region]:
    result = await db.execute(select(Region).order_by(col(Region.id)))
    return list(result.scalars().all())


async def list_events_in_region(db: AsyncSession, *, region_id: int) -> list[Event]:
    result = await db.execute(select(Event).where(col(Event.region_id) == region_id))
    return list(result.scalars().all())


async def list_users_in_region(db: AsyncSession, *, region_id: int) -> list[User]:
    result = await db.execute(select(User).where(col(User.region_id) == region_id))
    return list(result.scalars().all())
