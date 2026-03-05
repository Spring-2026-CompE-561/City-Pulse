"""Database configuration and session management (MySQL)."""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.config import settings
from app.region_map import REGION_SAN_DIEGO_ID

# Resolved URL is always set by config validator (MySQL)
_database_url: str = settings.database_url or ""

engine = create_async_engine(
    _database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables and seed San Diego region (id=0) if missing."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.execute(
            text("INSERT IGNORE INTO regions (id, name) VALUES (:id, :name)"),
            {"id": REGION_SAN_DIEGO_ID, "name": "San Diego"},
        )
