from starlette.requests import Request

import app.main as app_main_module


def _build_request() -> Request:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/test",
        "raw_path": b"/test",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 8000),
    }
    return Request(scope)


async def test_global_exception_handler_hides_details(monkeypatch):
    monkeypatch.setattr(app_main_module.settings, "debug", False)
    response = await app_main_module.global_exception_handler(
        _build_request(),
        RuntimeError("boom"),
    )
    assert response.status_code == 500
    assert response.body == b'{"detail":"Internal server error","success":false}'


async def test_global_exception_handler_shows_details_in_debug(monkeypatch):
    monkeypatch.setattr(app_main_module.settings, "debug", True)
    response = await app_main_module.global_exception_handler(
        _build_request(),
        RuntimeError("boom"),
    )
    assert response.status_code == 500
    assert b"RuntimeError: boom" in response.body
