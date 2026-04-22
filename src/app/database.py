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
from pathlib import Path
import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.config import settings
from app.ingestion.source_registry import build_default_sources
from app.models import Source
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
        # Backfill schema for older databases created before event category existed.
        event_category_column = await conn.execute(
            text("SHOW COLUMNS FROM events LIKE 'category'")
        )
        if event_category_column.first() is None:
            await conn.execute(
                text(
                    "ALTER TABLE events "
                    "ADD COLUMN category VARCHAR(100) NOT NULL DEFAULT 'Technology'"
                )
            )
        # Ensure San Diego exists. Prefer id=0 for consistency, but don't create
        # duplicates if older DBs already stored it under a different id.
        existing = await conn.execute(
            text(
                "SELECT id FROM regions "
                "WHERE LOWER(name) = LOWER(:name) "
                "ORDER BY id LIMIT 1"
            ),
            {"name": "San Diego"},
        )
        existing_id = existing.scalar_one_or_none()
        if existing_id is None:
            # MySQL treats 0 as AUTO_INCREMENT unless this mode is enabled.
            await conn.execute(
                text(
                    "SET SESSION sql_mode = CONCAT(@@SESSION.sql_mode, ',NO_AUTO_VALUE_ON_ZERO')"
                )
            )
            await conn.execute(
                text("INSERT IGNORE INTO regions (id, name) VALUES (:id, :name)"),
                {"id": REGION_SAN_DIEGO_ID, "name": "San Diego"},
            )
        await _run_sql_migrations(conn)

    async with async_session_maker() as session:
        await _seed_default_sources(session)
        await session.commit()


async def _run_sql_migrations(conn) -> None:
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    if not migrations_dir.exists():
        return
    await conn.execute(
        text(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "id VARCHAR(255) PRIMARY KEY,"
            "applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
    )
    existing_rows = await conn.execute(text("SELECT id FROM schema_migrations"))
    applied = {row[0] for row in existing_rows.all()}
    for path in sorted(migrations_dir.glob("*.sql")):
        migration_id = path.name
        if migration_id in applied:
            continue
        sql = path.read_text(encoding="utf-8").strip()
        if not sql:
            await conn.execute(
                text("INSERT INTO schema_migrations (id) VALUES (:id)"),
                {"id": migration_id},
            )
            continue
        statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
        for statement in statements:
            await _execute_migration_statement(conn, statement)
        await conn.execute(
            text("INSERT INTO schema_migrations (id) VALUES (:id)"),
            {"id": migration_id},
        )


async def _execute_migration_statement(conn: AsyncConnection, statement: str) -> None:
    column_match = re.search(
        r"ALTER TABLE\s+`?(\w+)`?\s+ADD COLUMN\s+IF\s+NOT\s+EXISTS\s+`?(\w+)`?\s+",
        statement,
        flags=re.IGNORECASE,
    )
    if column_match is not None:
        table_name, column_name = column_match.group(1), column_match.group(2)
        if await _column_exists(conn, table_name, column_name):
            return
        await conn.execute(text(_strip_if_not_exists(statement)))
        return

    index_match = re.search(
        r"ALTER TABLE\s+`?(\w+)`?\s+ADD INDEX\s+IF\s+NOT\s+EXISTS\s+`?(\w+)`?\s*\(",
        statement,
        flags=re.IGNORECASE,
    )
    if index_match is not None:
        table_name, index_name = index_match.group(1), index_match.group(2)
        if await _index_exists(conn, table_name, index_name):
            return
        await conn.execute(text(_strip_if_not_exists(statement)))
        return

    constraint_match = re.search(
        r"ALTER TABLE\s+`?(\w+)`?\s+ADD CONSTRAINT\s+`?(\w+)`?\s+",
        statement,
        flags=re.IGNORECASE,
    )
    if constraint_match is not None:
        table_name, constraint_name = constraint_match.group(1), constraint_match.group(2)
        if await _constraint_exists(conn, table_name, constraint_name):
            return

    canonical_url_unique_match = re.search(
        r"ALTER TABLE\s+`?events`?\s+ADD CONSTRAINT\s+`?uq_event_canonical_url`?\s+"
        r"UNIQUE\s*\(\s*`?canonical_url`?\s*\)",
        statement,
        flags=re.IGNORECASE,
    )
    if canonical_url_unique_match is not None:
        if await _index_exists(conn, "events", "uq_event_canonical_url"):
            return
        # utf8mb4 + long VARCHAR can exceed key-size limits for full-length UNIQUE indexes.
        await conn.execute(
            text("CREATE UNIQUE INDEX uq_event_canonical_url ON events (canonical_url(512))")
        )
        return

    await conn.execute(text(statement))


def _strip_if_not_exists(statement: str) -> str:
    return re.sub(r"\s+IF\s+NOT\s+EXISTS", "", statement, count=1, flags=re.IGNORECASE)


async def _column_exists(conn: AsyncConnection, table_name: str, column_name: str) -> bool:
    result = await conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = :table_name "
            "AND column_name = :column_name "
            "LIMIT 1"
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.first() is not None


async def _index_exists(conn: AsyncConnection, table_name: str, index_name: str) -> bool:
    result = await conn.execute(
        text(
            "SELECT 1 FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() "
            "AND table_name = :table_name "
            "AND index_name = :index_name "
            "LIMIT 1"
        ),
        {"table_name": table_name, "index_name": index_name},
    )
    return result.first() is not None


async def _constraint_exists(conn: AsyncConnection, table_name: str, constraint_name: str) -> bool:
    result = await conn.execute(
        text(
            "SELECT 1 FROM information_schema.table_constraints "
            "WHERE table_schema = DATABASE() "
            "AND table_name = :table_name "
            "AND constraint_name = :constraint_name "
            "LIMIT 1"
        ),
        {"table_name": table_name, "constraint_name": constraint_name},
    )
    return result.first() is not None


async def _seed_default_sources(session: AsyncSession) -> None:
    existing_count = await session.execute(
        text("SELECT COUNT(*) FROM sources WHERE region_id = :region_id"),
        {"region_id": REGION_SAN_DIEGO_ID},
    )
    if int(existing_count.scalar() or 0) > 0:
        return
    for source in build_default_sources():
        session.add(
            Source(
                region_id=source.region_id,
                name=source.name,
                domain=source.domain,
                base_url=source.base_url,
                source_type=source.source_type,
                category_hint=source.category_hint,
                neighborhood=source.neighborhood,
                is_active=source.is_active,
                crawl_allowed=source.crawl_allowed,
                crawl_delay_seconds=source.crawl_delay_seconds,
                rate_limit_per_min=source.rate_limit_per_min,
                attribution_text=source.attribution_text,
                robots_txt_url=source.robots_txt_url,
                terms_url=source.terms_url,
                parse_strategy=source.parse_strategy,
            )
        )
