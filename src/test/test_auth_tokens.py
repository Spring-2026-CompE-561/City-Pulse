from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


def test_access_token_round_trip():
    token = create_access_token(7)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "7"


def test_refresh_token_round_trip():
    token = create_refresh_token(11)
    payload = decode_refresh_token(token)
    assert payload is not None
    assert payload["sub"] == "11"


def test_access_decode_rejects_refresh_token():
    refresh = create_refresh_token(3)
    assert decode_access_token(refresh) is None

