from fastapi.testclient import TestClient

import app.main as app_main_module
from app.main import app


def test_root_endpoint_lists_api_prefixes(monkeypatch):
    async def _noop_init_db():
        return None

    monkeypatch.setattr(app_main_module, "init_db", _noop_init_db)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "City Pulse"
    assert "/api/health" in payload["endpoints"]
