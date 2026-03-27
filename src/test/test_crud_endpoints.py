from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import app.main as app_main_module
from app.main import app
from app.models import Event, User
from app.routes import events as events_router_module
from app.routes import users as users_router_module


async def _fake_get_db():
    yield AsyncMock()


async def _fake_current_user():
    return User(
        id=1,
        name="Ana",
        email="ana@example.com",
        password_hash="x",
        created_at=datetime.now(UTC),
        region_id=0,
    )


def _build_client(monkeypatch) -> TestClient:
    async def _noop_init_db():
        return None

    monkeypatch.setattr(app_main_module, "init_db", _noop_init_db)
    app.dependency_overrides[events_router_module.get_db] = _fake_get_db
    app.dependency_overrides[users_router_module.get_db] = _fake_get_db
    app.dependency_overrides[events_router_module.get_current_user_required] = _fake_current_user
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
    async def _fake_list_events(_db, region_id, skip, limit, category=None):
        return [
            Event(
                id=10,
                region_id=region_id,
                user_id=1,
                title="Picnic",
                category="Food & Drink",
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
    assert items[0]["category"] == "Food & Drink"


def test_list_event_categories_endpoint(monkeypatch):
    client = _build_client(monkeypatch)
    response = client.get("/api/events/categories")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    options = response.json()["options"]
    assert "All Categories" in options
    assert "Technology" in options


def test_list_events_rejects_invalid_category(monkeypatch):
    client = _build_client(monkeypatch)
    response = client.get("/api/events?category=UnknownCategory")
    app.dependency_overrides.clear()
    assert response.status_code == 400


def test_create_event_rejects_other_user(monkeypatch):
    async def _fake_create_event(*_args, **_kwargs):  # pragma: no cover
        raise AssertionError("create_event_row should not be called")

    monkeypatch.setattr(events_router_module, "create_event_row", _fake_create_event)
    client = _build_client(monkeypatch)
    response = client.post(
        "/api/events/",
        json={
            "user_id": 2,
            "title": "New Event",
            "category": "Technology",
            "content": "body",
        },
    )
    app.dependency_overrides.clear()
    assert response.status_code == 403


def test_update_event_not_found(monkeypatch):
    async def _fake_get_event_by_id(_db, _event_id):
        return None

    monkeypatch.setattr(events_router_module, "get_event_by_id", _fake_get_event_by_id)
    client = _build_client(monkeypatch)
    response = client.put(
        "/api/events/999",
        json={"title": "Updated", "category": "Business", "content": "new"},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 404

