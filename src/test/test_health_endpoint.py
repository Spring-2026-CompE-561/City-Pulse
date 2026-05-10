from fastapi.testclient import TestClient

import app.main as app_main_module
from app.main import app


def test_health_endpoint_returns_ok(monkeypatch):
    async def _noop_init_db():
        return None

    monkeypatch.setattr(app_main_module, "init_db", _noop_init_db)
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "City Pulse API",
        "database": "ready",
    }
