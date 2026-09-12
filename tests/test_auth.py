import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.auth import require_user


def _request(scope=None):
    scope = scope or {"type": "http", "method": "GET", "path": "/", "headers": []}
    return Request(scope)


def test_auth_disabled_allows_local_user(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "false")
    user = require_user(_request())
    assert user["sub"] == "local"


def test_auth_enabled_requires_session(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "true")
    request = _request()
    request.scope["session"] = {}
    with pytest.raises(HTTPException) as exc:
        require_user(request)
    assert exc.value.status_code == 401
