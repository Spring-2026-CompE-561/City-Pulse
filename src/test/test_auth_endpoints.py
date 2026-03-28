from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

#We need these modules to swap out real logic for mocks during test
import app.main as app_main_module
from app.main import app
from app.routes import auth as auth_router_module


#This is a helper to bypass real database connections
#We just yield a mock object becase we donot want tests hitting a real DB
async def _fake_get_db():
    yield AsyncMock()

#Setting up the test cliet
#We are monkeypatching the init_db so the app doesnot try to connect to anything on startup
def _build_client(monkeypatch) -> TestClient:
    async def _noop_init_db():
        return None

    monkeypatch.setattr(app_main_module, "init_db", _noop_init_db)

    #FastAPI is cool because we can override dependencies(like get_db)
    #globally for the duration of the test
    app.dependency_overrides[auth_router_module.get_db] = _fake_get_db
    return TestClient(app)


def test_login_returns_token_pair(monkeypatch):
    #####
    #Scenario: User Provides valid crendentials
    #Expected: We should get a nice pair of tokens back
    ######
    async def _fake_login_user(_db, _payload):
        return {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
        }

    #Inject our fake login logic into the router modle
    monkeypatch.setattr(auth_router_module, "login_user", _fake_login_user)
    client = _build_client(monkeypatch)
    response = client.post("/api/auth/login", json={"email": "u@example.com", "password": "pw"})
    
    #Always clean up overrides so we donot pollute other tests
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(monkeypatch):
    #####
    #Scenario: User messes up their password
    #Expected: We should get a 401 Unauthorized response
    ######
    
    #Here we simulate the 'user not found' or 'wrong password' case by returning None 
    async def _fake_login_user(_db, _payload):
        return None

    monkeypatch.setattr(auth_router_module, "login_user", _fake_login_user)
    client = _build_client(monkeypatch)
    response = client.post("/api/auth/login", json={"email": "u@example.com", "password": "bad"})
    app.dependency_overrides.clear()
    assert response.status_code == 401


def test_me_requires_bearer_token(monkeypatch):
    #####
    #Scenario: User tries to access /me without providing a token
    #Expected: We should get a 401 Unauthorized response
    ######
    client = _build_client(monkeypatch)

    # No headers provided here, so it should fail autimatically
    response = client.get("/api/auth/me")
    app.dependency_overrides.clear()
    assert response.status_code == 401

