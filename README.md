# City Pulse

Location-based events + trends platform (backend API). Users can register/login, create events (currently **San Diego only**), interact (likes/comments/attending), and view a ranked “trending” list driven by interactions. The platform now supports source-based ingestion for nightlife/music listings and official-only partner submissions for public/charity/flea events.

---

## Tech stack

| Layer        | Technology |
|-------------|------------|
| API         | [FastAPI](https://fastapi.tiangolo.com/) |
| Server      | [Uvicorn](https://www.uvicorn.org/) |
| ORM / DB    | [SQLModel](https://sqlmodel.tiangolo.com/) (on top of [SQLAlchemy](https://docs.sqlalchemy.org/) 2.x, async) + [asyncmy](https://github.com/long2ice/asyncmy) (MySQL). |
| Validation   | [Pydantic](https://docs.pydantic.dev/) + [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Auth        | JWT access + refresh tokens |
| Code quality | [Ruff](https://docs.astral.sh/ruff/), [Black](https://black.readthedocs.io/), [pre-commit](https://pre-commit.com/) |

---

## Project structure

```
City-Pulse/
├── pyproject.toml
├── requirements.txt
├── README.md
├── postman/
│   └── City-Pulse.postman_collection.json
└── src/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── api/
    │   │   └── v1/
    │   │       ├── __init__.py
    │   │       └── routes.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── auth.py
    │   │   ├── database.py
    │   │   ├── dependencies.py
    │   │   └── settings.py
    │   ├── routes/
    │   ├── repository/
    │   ├── routers/
    │   ├── repositories/
    │   ├── auth.py
    │   ├── config.py
    │   ├── database.py
    │   ├── models.py
    │   ├── schemas.py
    │   └── services/
    └── test/
        ├── test_auth_endpoints.py
        ├── test_auth_tokens.py
        ├── test_crud_endpoints.py
        └── test_event_repository.py
```

---

## Run the project

### Local setup (Windows / PowerShell)

1. **Create and activate a virtual environment**:

   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies** (from repo root):

   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

3. **Configure environment** (MySQL):

   - Set a full `DATABASE_URL`, or set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`.
   - You can use a `.env` file in the repo root (loaded automatically via Pydantic Settings).

4. **Run the API** (from repo root, with `src` on `PYTHONPATH`):

   ```bash
   $env:PYTHONPATH="src"
   uvicorn app.main:app --reload
   ```

5. **Open**:

   - API root: `http://127.0.0.1:8000/`
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

6. **Run tests**:

   ```bash
   pytest
   ```

---

## Optional: pre-commit

```bash
pip install pre-commit
pre-commit install
```

After that, Ruff and Black run automatically on commit.

---

## Environment

Create a `.env` file in the repo root (or export env vars) to configure the database and token lifetimes.

| Variable        | Default / built value             | Description |
|----------------|-----------------------------------|-------------|
| `DATABASE_URL` | *(optional)* | Full DB URL override (recommended). Example: `mysql+asyncmy://user:pass@localhost:3306/city_pulse?charset=utf8mb4` |
| `MYSQL_HOST`   | `localhost`  | MySQL host (used only if `DATABASE_URL` is not set). |
| `MYSQL_PORT`   | `3306`       | MySQL port. |
| `MYSQL_USER`   | *(varies)*   | MySQL user. |
| `MYSQL_PASSWORD` | *(required)* | MySQL password. |
| `MYSQL_DATABASE` | `city_pulse` | MySQL database name. |
| `DEBUG`        | `false`      | If true, returns more detailed 500 errors and enables verbose debugging. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token expiry (minutes). |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token expiry (days). |
| `JWT_SECRET_KEY` | `change-me-in-production-at-least-32-bytes` | Secret key used to sign and verify JWT access/refresh tokens. |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm. |
| `CORS_ALLOW_ORIGINS` | `*` | `*` or comma-separated allowed origins for CORS. |
| `INGEST_API_KEY` | *(required for admin ingestion endpoints)* | Header `X-Ingest-Key` value for source/ingest moderation routes. |
| `INGEST_SCHEDULER_ENABLED` | `false` | Enables periodic ingestion in app process. |
| `INGEST_SCHEDULER_INTERVAL_MINUTES` | `60` | Scheduler interval, minimum 5 minutes. |

**Startup behavior**: on app startup it creates tables (if missing) and seeds the default region data.

---

## API overview

### Service discovery

- **`GET /`**: service info + quick list of API prefixes
- **`GET /docs`**: Swagger UI
- **`GET /openapi.json`**: OpenAPI schema

### Auth (`/api/auth`)

- **`POST /api/auth/register`**: create account, returns `{ access_token, refresh_token, token_type }`
- **`POST /api/auth/login`**: returns `{ access_token, refresh_token, token_type }`
- **`POST /api/auth/refresh`**: exchange refresh token for a new token pair
- **`GET /api/auth/me`**: current user (requires `Authorization: Bearer <access_token>`)

### Users (`/api/users`)

- **`GET /api/users?skip=0&limit=50`**
- **`GET /api/users/{id}`**
- **`PUT /api/users/{id}`**: update name/email/city_location (requires `current_password`; city_location currently only supports “san diego”)
- **`DELETE /api/users/{id}`**

### Regions (`/api/regions`)

- **`GET /api/regions`**
- **`GET /api/regions/{region_id_or_name}/events`**: `region_id_or_name` can be `0`, `san diego`, or `san-diego`
- **`GET /api/regions/{region_id_or_name}/users`**

### Events (`/api/events`)

- **`GET /api/events?region=san%20diego&skip=0&limit=50`**
- **`GET /api/events?region=san%20diego&category=All%20Categories&neighborhood=North%20Park&starts_after=2026-04-21T00:00:00Z&skip=0&limit=50`**
- **`GET /api/events/categories`**: dropdown options (`All Categories`, `Technology`, `Arts & Culture`, `Environment`, `Entertainment`, `Business`, `Food & Drink`, `Health & Wellness`, `Music`, `Nightlife`, `Charity & Causes`, `Community`)
- **`GET /api/events/{id}`**
- **`POST /api/events`**: create event for a user (user must be in the San Diego region) with optional event metadata (`event_start_at`, `venue_name`, `neighborhood`, `price_info`, etc.)
- **`PUT /api/events/{id}`**
- **`DELETE /api/events/{id}`**

### Interactions (`/api/interactions`)

- **`GET /api/interactions?region=san%20diego&category=Nightlife&neighborhood=Gaslamp&starts_after=...&skip=0&limit=50`**: returns events with likes/comments/attendance counts + comment list
- **`PUT /api/interactions/events/{event_id}/likes`**
- **`DELETE /api/interactions/events/{event_id}/likes?user_id=...`**
- **`PUT /api/interactions/events/{event_id}/comments`**
- **`DELETE /api/interactions/events/{event_id}/comments/{comment_id}?user_id=...`**
- **`PUT /api/interactions/events/{event_id}/attending`**
- **`DELETE /api/interactions/events/{event_id}/attending?user_id=...`**

### Trends (`/api/trends`)

- **`GET /api/trends?region=san%20diego&skip=0&limit=50`**: ranked by interactions (attendance first, then comments, then likes)
- **`POST /api/trends`**: rebuild trend list from current interactions (**requires `X-Ingest-Key`**)
- **`PUT /api/trends`**: upsert an event in trends and reorder (**requires `X-Ingest-Key`**)

### Sources (`/api/sources`)

- **`GET /api/sources`**: list active configured sources (requires `X-Ingest-Key`)
- **`GET /api/sources/{source_id}`**: source details (requires `X-Ingest-Key`)

### Ingestion (`/api/ingest`)

- **`POST /api/ingest/run`**: run ingestion for one source or filtered area (requires `X-Ingest-Key`)
- **`POST /api/ingest/run-all`**: run ingestion for all active sources (requires `X-Ingest-Key`)
- **`GET /api/ingest/runs`**: recent ingestion runs and parser errors (requires `X-Ingest-Key`)

### Partner submissions (`/api/partner-submissions`)

- **`POST /api/partner-submissions`**: authenticated submission path for Instagram/public event links (official-only workflow)
- **`GET /api/partner-submissions`**: moderation queue view (requires `X-Ingest-Key`)
- **`PUT /api/partner-submissions/{submission_id}/review`**: approve/reject and optionally publish event (requires `X-Ingest-Key`)

---

## Ingestion and migration workflow

- SQL migrations live in `src/migrations/*.sql`.
- On startup, `init_db()` creates `schema_migrations` and applies new SQL scripts once.
- Default San Diego nightlife/music source records are seeded when no sources exist.
- Compliance rules are documented in `SCRAPING_POLICY.md`.

---

## Postman testing

- Import `postman/City-Pulse.postman_collection.json`.
- Set `base_url` to your local API URL.
- Run the auth flow (`Register` -> `Login` -> `Get Current User`).
- Run `List Event Categories`, `List Events (All Categories)`, and `List Events (Invalid Category - expect 400)` to verify validation and graceful error handling.
- Use Swagger for the remaining CRUD endpoints.

---

## Submission checklist

- Include `README.md`, `pyproject.toml`, and `requirements.txt`.
- Ensure tests pass locally with `pytest`.
- Package the project as a `.zip` from the repository root for submission.

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
