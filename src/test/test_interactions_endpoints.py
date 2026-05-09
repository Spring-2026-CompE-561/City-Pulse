from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import app.main as app_main_module
from app.main import app
from app.models import Event, EventComment, User
from app.routes import interactions as interactions_router_module


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


async def _fake_other_user():
    return User(
        id=2,
        name="Beto",
        email="beto@example.com",
        password_hash="x",
        created_at=datetime.now(UTC),
        region_id=0,
    )


def _build_client(monkeypatch, *, use_other_user: bool = False) -> TestClient:
    async def _noop_init_db():
        return None

    monkeypatch.setattr(app_main_module, "init_db", _noop_init_db)
    app.dependency_overrides[interactions_router_module.get_db] = _fake_get_db
    app.dependency_overrides[interactions_router_module.get_current_user_required] = (
        _fake_other_user if use_other_user else _fake_current_user
    )
    return TestClient(app)


def test_delete_comment_succeeds_for_comment_owner(monkeypatch):
    called = {"remove": False}

    async def _fake_get_event_by_id(_db, _event_id):
        return Event(
            id=10,
            region_id=0,
            user_id=1,
            title="Picnic",
            category="Food & Drink",
            content="Sunday",
            created_at=datetime.now(UTC),
        )

    async def _fake_get_comment_by_id(_db, comment_id):
        return EventComment(
            id=comment_id,
            user_id=1,
            event_id=10,
            text="hello",
            created_at=datetime.now(UTC),
        )

    async def _fake_remove_comment(_db, *, comment):
        called["remove"] = True
        assert comment.id == 5

    monkeypatch.setattr(interactions_router_module, "get_event_by_id", _fake_get_event_by_id)
    monkeypatch.setattr(interactions_router_module, "get_comment_by_id", _fake_get_comment_by_id)
    monkeypatch.setattr(interactions_router_module, "remove_comment_row", _fake_remove_comment)

    client = _build_client(monkeypatch)
    response = client.delete("/api/interactions/events/10/comments/5")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert called["remove"] is True


def test_delete_comment_forbidden_for_non_owner(monkeypatch):
    async def _fake_get_event_by_id(_db, _event_id):
        return Event(
            id=10,
            region_id=0,
            user_id=1,
            title="Picnic",
            category="Food & Drink",
            content="Sunday",
            created_at=datetime.now(UTC),
        )

    async def _fake_get_comment_by_id(_db, comment_id):
        return EventComment(
            id=comment_id,
            user_id=1,
            event_id=10,
            text="hello",
            created_at=datetime.now(UTC),
        )

    async def _fake_remove_comment(*_args, **_kwargs):  # pragma: no cover
        raise AssertionError("remove_comment_row should not be called")

    monkeypatch.setattr(interactions_router_module, "get_event_by_id", _fake_get_event_by_id)
    monkeypatch.setattr(interactions_router_module, "get_comment_by_id", _fake_get_comment_by_id)
    monkeypatch.setattr(interactions_router_module, "remove_comment_row", _fake_remove_comment)

    client = _build_client(monkeypatch, use_other_user=True)
    response = client.delete("/api/interactions/events/10/comments/5")
    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_list_interactions_filters_with_current_time_and_cleanup(monkeypatch):
    called = {"cleanup": False, "active_after_seen": False}

    async def _fake_list_events_by_region(
        _db,
        *,
        region_id,
        skip,
        limit,
        category=None,
        neighborhood=None,
        starts_after=None,
        starts_before=None,
        active_after=None,
    ):
        assert region_id == 0
        assert skip == 0
        assert limit == 50
        assert category is None
        assert neighborhood is None
        assert starts_after is None
        assert starts_before is None
        assert active_after is not None
        assert active_after.tzinfo is not None
        called["active_after_seen"] = True
        return [
            Event(
                id=10,
                region_id=0,
                user_id=1,
                title="Picnic",
                category="Food & Drink",
                content="Sunday",
                created_at=datetime.now(UTC),
            )
        ]

    async def _fake_delete_past_events(_db, *, region_id, retention_cutoff):
        assert region_id == 0
        assert retention_cutoff.tzinfo is not None
        called["cleanup"] = True
        return 0

    async def _fake_get_counts(_db, *, event_id):
        assert event_id == 10
        return 0, 0, 0

    async def _fake_list_comments(_db, *, event_id):
        assert event_id == 10
        return []

    monkeypatch.setattr(
        interactions_router_module,
        "list_events_by_region",
        _fake_list_events_by_region,
    )
    monkeypatch.setattr(
        interactions_router_module,
        "delete_past_events_older_than",
        _fake_delete_past_events,
    )
    monkeypatch.setattr(
        interactions_router_module,
        "get_event_interaction_counts",
        _fake_get_counts,
    )
    monkeypatch.setattr(
        interactions_router_module,
        "list_comments_for_event",
        _fake_list_comments,
    )
    client = _build_client(monkeypatch)
    response = client.get("/api/interactions/")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == 10
    assert called["cleanup"] is True
    assert called["active_after_seen"] is True
