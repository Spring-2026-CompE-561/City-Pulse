from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import Source


async def list_active_sources(
    db: AsyncSession,
    *,
    region_id: int,
    category_hint: str | None = None,
    neighborhood: str | None = None,
) -> list[Source]:
    query = select(Source).where(
        col(Source.region_id) == region_id,
        col(Source.is_active) == True,  # noqa: E712
    )
    if category_hint is not None:
        query = query.where(col(Source.category_hint) == category_hint)
    if neighborhood is not None:
        query = query.where(col(Source.neighborhood) == neighborhood)
    result = await db.execute(query.order_by(col(Source.name)))
    return list(result.scalars().all())


async def get_source_by_id(db: AsyncSession, source_id: int) -> Source | None:
    return await db.get(Source, source_id)


async def create_source(db: AsyncSession, source: Source) -> Source:
    db.add(source)
    await db.flush()
    await db.refresh(source)
    return source
