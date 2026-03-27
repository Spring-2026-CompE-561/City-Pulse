from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import app.main as app_main_module
from app.main import app
from app.routers import auth as auth_router_module


async def _fake_get_db():
    yield AsyncMock()


def _build_client(monkeypatch) -> TestClient:
    async def _noop_init_db():
        return None

    monkeypatch.setattr(app_main_module, "init_db", _noop_init_db)
    app.dependency_overrides[auth_router_module.get_db] = _fake_get_db
    return TestClient(app)


def test_login_returns_token_pair(monkeypatch):
    async def _fake_login_user(_db, _payload):
        return {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
        }

    monkeypatch.setattr(auth_router_module, "login_user", _fake_login_user)
    client = _build_client(monkeypatch)
    response = client.post("/api/auth/login", json={"email": "u@example.com", "password": "pw"})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(monkeypatch):
    async def _fake_login_user(_db, _payload):
        return None

    monkeypatch.setattr(auth_router_module, "login_user", _fake_login_user)
    client = _build_client(monkeypatch)
    response = client.post("/api/auth/login", json={"email": "u@example.com", "password": "bad"})
    app.dependency_overrides.clear()
    assert response.status_code == 401


def test_me_requires_bearer_token(monkeypatch):
    client = _build_client(monkeypatch)
    response = client.get("/api/auth/me")
    app.dependency_overrides.clear()
    assert response.status_code == 401

