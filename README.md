# City Pulse

Location-based trend aggregation web application. Informs users about significant events, market trends, and discussions in their region in real time (e.g. *“heatwave San Diego”*).

---

## Tech stack

| Layer        | Technology |
|-------------|------------|
| API         | [FastAPI](https://fastapi.tiangolo.com/) |
| Server      | [Uvicorn](https://www.uvicorn.org/) |
| ORM / DB    | [SQLAlchemy](https://docs.sqlalchemy.org/) 2.x (async) + [aiosqlite](https://aiosqlite.readthedocs.io/) |
| Validation   | [Pydantic](https://docs.pydantic.dev/) + [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Code quality | [Ruff](https://docs.astral.sh/ruff/), [Black](https://black.readthedocs.io/), [pre-commit](https://pre-commit.com/) |

---

## Project structure

```
City-Pulse/
├── py-project.toml       # Project config, dependencies, tools
├── pre-commit-config.yml # Pre-commit hooks (Ruff, Black)
├── .vscode/
│   └── settings.json     # Python interpreter & analysis path
└── src/
    ├── app/              # Main application package
    │   ├── __init__.py   # Exposes app
    │   ├── main.py       # FastAPI app, lifespan, routers
    │   ├── config.py     # Settings (env / .env)
    │   ├── database.py   # Async engine, session, init_db
    │   ├── models.py     # SQLAlchemy models (User, Region, Event)
    │   ├── schemas.py    # Pydantic request/response schemas
    │   └── routers/      # API route modules
    │       ├── users.py
    │       ├── regions.py
    │       ├── events.py
    │       └── trends.py
    └── test/
        └── main.py       # Tests
```

---

## What each part does

### `py-project.toml`

- **Project metadata**: name, version, description, Python ≥3.11.
- **Dependencies**: FastAPI, Uvicorn, SQLAlchemy, Pydantic, Pydantic-Settings, aiosqlite.
- **Optional dev**: pytest, pytest-asyncio, httpx, ruff, black, pre-commit.
- **Build**: Hatch; package lives in `src/app`.
- **Tools**: Ruff and Black config (line length, target version), pytest asyncio and test path.

**Resources:** [PyPA – pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) · [Hatch](https://hatch.pypa.io/)

---

### `pre-commit-config.yml`

Runs before each commit:

- **Ruff**: lint and auto-fix.
- **Black**: format code.

**Resources:** [pre-commit](https://pre-commit.com/) · [Ruff pre-commit](https://docs.astral.sh/ruff/integration/#pre-commit) · [Black integration](https://black.readthedocs.io/en/stable/integrations/source_version_control.html)

---

### `src/app/config.py`

- Loads settings from environment or a `.env` file.
- Defines `debug` and `database_url` (default: SQLite with aiosqlite).
- Single `settings` instance used across the app.

**Resources:** [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

### `src/app/database.py`

- **Engine**: async SQLAlchemy engine from `config.database_url`.
- **Session**: async session factory and `get_db()` dependency for request-scoped sessions (commit/rollback/close).
- **init_db()**: creates all tables (called on app startup in `main.py`).

**Resources:** [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) · [AsyncSession](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.ext.asyncio.AsyncSession)

---

### `src/app/models.py`

SQLAlchemy ORM models:

- **User**: `id`, `created_at`, `email`, `display_name`; many-to-many with regions via `user_regions`.
- **Region**: `id`, `name`, `slug` (e.g. `san-diego`), `created_at`; has events and users.
- **UserRegion**: join table for user ↔ region.
- **Event**: `id`, `region_id`, `timestamp`, `category`, `sentiment_score`, `source_url`, `raw_data` (JSON), `title`, `summary`.

**Resources:** [SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/) · [Declarative mapping](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#declarative-mapping)

---

### `src/app/schemas.py`

Pydantic models for API:

- **Users**: UserCreate, UserRead.
- **Regions**: RegionBase/RegionCreate/RegionRead (slug pattern e.g. `san-diego`).
- **Events**: EventBase/EventCreate/EventRead (category, sentiment, source_url, raw_data, etc.).
- **Trends**: TrendItem (topic, region_slug, event_count, avg_sentiment, sample_title/source_url), TrendList.

**Resources:** [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) · [Field](https://docs.pydantic.dev/latest/concepts/fields/)

---

### `src/app/main.py`

- **FastAPI app**: title “City Pulse”, description, version, lifespan.
- **Lifespan**: calls `init_db()` on startup.
- **Routers**: `users`, `regions`, `events`, `trends` mounted at `/users`, `/regions`, `/events`, `/trends`.
- **Root**: `GET /` returns service info and links to `/docs`, `/openapi.json`, and the main endpoints.

**Resources:** [FastAPI app](https://fastapi.tiangolo.com/tutorial/first-steps/) · [Lifespan](https://fastapi.tiangolo.com/advanced/events/) · [APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

---

### `src/app/routers/`

| Router     | Prefix   | Purpose |
|-----------|----------|--------|
| **users** | `/users` | List, get by id, create users. |
| **regions** | `/regions` | List (optional filter by `slug`), get by id, create regions. |
| **events** | `/events` | List (optional `region_id`, `category`), get by id, create events (with timestamp, category, sentiment, source_url, raw_data). |
| **trends** | `/trends` | Aggregated trends by topic and region (e.g. “heatwave san diego”): optional `region_slug`, `category`, `limit`. |

**Resources:** [FastAPI dependency injection](https://fastapi.tiangolo.com/tutorial/dependencies/) (e.g. `get_db`) · [Query parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

---

## Run the project

1. **Create and use a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies** (from repo root):

   ```bash
   pip install -e .
   ```

   If your project file is `py-project.toml` and your tool expects `pyproject.toml`, either rename it or install with:

   ```bash
   pip install fastapi "uvicorn[standard]" sqlalchemy pydantic pydantic-settings aiosqlite
   ```

3. **Run the API** (from repo root, with `src` on `PYTHONPATH`):

   ```bash
   # Windows (PowerShell)
   $env:PYTHONPATH="src"; uvicorn app.main:app --reload

   # macOS/Linux
   PYTHONPATH=src uvicorn app.main:app --reload
   ```

4. **Open**: [http://127.0.0.1:8000](http://127.0.0.1:8000) — root info.  
   **Interactive API docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Optional: pre-commit

```bash
pip install pre-commit
pre-commit install
```

After that, Ruff and Black run automatically on commit.

---

## Environment

| Variable        | Default                          | Description                |
|----------------|-----------------------------------|----------------------------|
| `DEBUG`        | `false`                           | Enable SQL echo / debug.   |
| `DATABASE_URL` | `sqlite+aiosqlite:///./city_pulse.db` | Async DB URL. Use `.env` to override. |

---

## API overview

- **`GET /`** — Service name, link to docs, list of endpoints.
- **`GET /docs`** — Swagger UI.
- **`GET /openapi.json`** — OpenAPI schema.
- **`/users`** — CRUD-style: list, get, create.
- **`/regions`** — List (filter by `slug`), get, create.
- **`/events`** — List (filter by `region_id`, `category`), get, create.
- **`/trends`** — Aggregated trends; query params: `region_slug`, `category`, `limit`.

---

## Resources (links)

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic](https://docs.pydantic.dev/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Ruff](https://docs.astral.sh/ruff/)
- [Black](https://black.readthedocs.io/)
- [pre-commit](https://pre-commit.com/)
- [Hatch (build)](https://hatch.pypa.io/)
- [PyPA – pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
