"""Database configuration and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Base
from app.region_map import REGION_SAN_DIEGO_ID

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

if "sqlite" in settings.database_url:

    @event.listens_for(engine.sync_engine, "connect")
    def _sqlite_fk_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

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


async def _ensure_users_region_id(conn) -> None:
    """Add region_id to users table if missing (migration for existing DBs)."""
    if "sqlite" not in str(engine.url):
        return
    result = await conn.execute(text("PRAGMA table_info(users)"))
    rows = result.all()
    if not rows:
        return
    columns = [row[1] for row in rows]
    if "region_id" in columns:
        return
    await conn.execute(text("ALTER TABLE users ADD COLUMN region_id INTEGER REFERENCES regions(id)"))


async def _ensure_users_name_column(conn) -> None:
    """Add name column to users if missing (old DBs had display_name). Copy display_name -> name."""
    if "sqlite" not in str(engine.url):
        return
    result = await conn.execute(text("PRAGMA table_info(users)"))
    rows = result.all()
    if not rows:
        return
    columns = [row[1] for row in rows]
    if "name" in columns:
        return
    await conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(255)"))
    if "display_name" in columns:
        await conn.execute(text("UPDATE users SET name = COALESCE(display_name, '') WHERE name IS NULL"))


async def _ensure_trend_count_columns(conn) -> None:
    """Add attendance_count, comments_count, likes_count to trends if missing."""
    if "sqlite" not in str(engine.url):
        return
    result = await conn.execute(text("PRAGMA table_info(trends)"))
    rows = result.all()
    if not rows:
        return
    columns = [row[1] for row in rows]
    if "attendance_count" not in columns:
        await conn.execute(text("ALTER TABLE trends ADD COLUMN attendance_count INTEGER NOT NULL DEFAULT 0"))
    if "comments_count" not in columns:
        await conn.execute(text("ALTER TABLE trends ADD COLUMN comments_count INTEGER NOT NULL DEFAULT 0"))
    if "likes_count" not in columns:
        await conn.execute(text("ALTER TABLE trends ADD COLUMN likes_count INTEGER NOT NULL DEFAULT 0"))


async def init_db() -> None:
    """Create all tables, migrate if needed, and seed San Diego region (id=0) if missing."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_users_region_id(conn)
        await _ensure_users_name_column(conn)
        await _ensure_trend_count_columns(conn)
        await conn.execute(
            text("INSERT OR IGNORE INTO regions (id, name) VALUES (:id, :name)"),
            {"id": REGION_SAN_DIEGO_ID, "name": "San Diego"},
        )
