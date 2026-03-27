from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import app.main as app_main_module
from app.main import app
from app.models import Event, User
from app.routers import events as events_router_module
from app.routers import users as users_router_module


async def _fake_get_db():
    yield AsyncMock()


def _build_client(monkeypatch) -> TestClient:
    async def _noop_init_db():
        return None

    monkeypatch.setattr(app_main_module, "init_db", _noop_init_db)
    app.dependency_overrides[events_router_module.get_db] = _fake_get_db
    app.dependency_overrides[users_router_module.get_db] = _fake_get_db
    return TestClient(app)


def test_list_users_endpoint(monkeypatch):
    async def _fake_list_users(_db, skip, limit):
        return [
            User(
                id=1,
                name="Ana",
                email="ana@example.com",
                password_hash="x",
                created_at=datetime.now(UTC),
                region_id=0,
            )
        ]

    monkeypatch.setattr(users_router_module, "list_user_rows", _fake_list_users)
    client = _build_client(monkeypatch)
    response = client.get("/api/users/")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["users"][0]["email"] == "ana@example.com"


def test_list_events_endpoint(monkeypatch):
    async def _fake_list_events(_db, region_id, skip, limit):
        return [
            Event(
                id=10,
                region_id=region_id,
                user_id=1,
                title="Picnic",
                content="Sunday",
                created_at=datetime.now(UTC),
            )
        ]

    monkeypatch.setattr(events_router_module, "list_events_by_region", _fake_list_events)
    client = _build_client(monkeypatch)
    response = client.get("/api/events")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["title"] == "Picnic"

