"""
Database configuration and session management (MySQL).

What lives here
- The async SQLAlchemy engine used by SQLModel/SQLAlchemy for all DB I/O.
- An async session factory (`async_session_maker`) used to create per-request sessions.
- FastAPI dependencies:
  - `get_db()` yields an `AsyncSession` and commits/rolls back automatically.
- Startup helper:
  - `init_db()` creates tables and seeds the default region row.

Called by / import relationships
- `app.main.lifespan()` calls `init_db()` during application startup.
- Routers/services import `get_db` and use it via `Depends(get_db)` for DB access.
- `settings` (DB URL + debug) come from `app.config`.
"""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.config import settings
from app.region_map import REGION_SAN_DIEGO_ID

# Resolved URL is set by the `Settings` validator (MySQL). Kept module-private on purpose.
# Used by: `create_async_engine(...)` below.
_database_url: str = settings.database_url or ""

# The global async engine shared across the app process.
# Used by: `async_sessionmaker(...)` to create request sessions.
engine = create_async_engine(
    _database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory used by `get_db()` to create an `AsyncSession` per request.
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    How it behaves
    - Opens a session for the request.
    - Yields it to the route handler / service code.
    - If the request finishes successfully, commits the transaction.
    - If an exception occurs, rolls back and re-raises.
    - Always closes the session.

    Called by
    - Routers and dependencies via `Depends(get_db)`.
    """
    async with async_session_maker() as session:
        try:
            # The caller uses this session for all ORM queries/flushes.
            yield session
            # If no exception was raised, persist changes.
            await session.commit()
        except Exception:
            # On any error, undo partial work for this request.
            await session.rollback()
            raise
        finally:
            # Always release DB connections back to the pool.
            await session.close()


async def init_db() -> None:
    """
    Initialize database schema and seed required data.

    What it does
    - Creates all tables defined in `SQLModel.metadata` (models imported in `app.main`).
    - Inserts the default Region row for San Diego (id=0) if missing.

    Called by
    - `app.main.lifespan()` during application startup.
    """
    async with engine.begin() as conn:
        # Create all tables for all SQLModel models (Region, User, Event, etc).
        await conn.run_sync(SQLModel.metadata.create_all)
        # Insert the default region row if it doesn't exist (MySQL `INSERT IGNORE`).
        await conn.execute(
            text("INSERT IGNORE INTO regions (id, name) VALUES (:id, :name)"),
            {"id": REGION_SAN_DIEGO_ID, "name": "San Diego"},
        )
