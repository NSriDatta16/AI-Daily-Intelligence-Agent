from __future__ import annotations

import os
from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse


oauth = OAuth()


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _enabled() -> bool:
    return _env("AUTH_ENABLED", "false").lower() == "true"


def _configured() -> bool:
    return all(
        [
            _enabled(),
            _env("ENTRA_TENANT_ID"),
            _env("ENTRA_CLIENT_ID"),
            _env("ENTRA_CLIENT_SECRET"),
            _env("AUTH_SESSION_SECRET"),
        ]
    )


def _client():
    if not _configured():
        raise RuntimeError(
            "Entra authentication is enabled but its configuration is incomplete. "
            "Set ENTRA_TENANT_ID, ENTRA_CLIENT_ID, ENTRA_CLIENT_SECRET and AUTH_SESSION_SECRET."
        )
    return oauth.register(
        name="entra",
        client_id=_env("ENTRA_CLIENT_ID"),
        client_secret=_env("ENTRA_CLIENT_SECRET"),
        server_metadata_url=(
            f"https://login.microsoftonline.com/{_env('ENTRA_TENANT_ID')}"
            "/v2.0/.well-known/openid-configuration"
        ),
        client_kwargs={"scope": "openid profile email"},
    )


def session_secret() -> str:
    return _env("AUTH_SESSION_SECRET")


def cookie_secure() -> bool:
    return _env("AUTH_COOKIE_SECURE", "true").lower() == "true"


def _allowed(user: dict[str, Any]) -> bool:
    allowed = {
        value.strip().lower()
        for value in _env("AUTH_ALLOWED_EMAILS").split(",")
        if value.strip()
    }
    if not allowed:
        return True
    email = str(user.get("email") or user.get("preferred_username") or "").lower()
    return email in allowed


async def login(request: Request) -> RedirectResponse:
    client = _client()
    redirect_uri = _env("AUTH_REDIRECT_URI") or str(request.url_for("auth_callback"))
    return await client.authorize_redirect(request, redirect_uri)


async def callback(request: Request) -> RedirectResponse:
    client = _client()
    token = await client.authorize_access_token(request)
    userinfo = dict(token.get("userinfo") or {})
    if not userinfo:
        userinfo = dict(await client.userinfo(token=token))

    if not _allowed(userinfo):
        request.session.clear()
        raise HTTPException(status_code=403, detail="This account is not authorized for this dashboard")

    request.session["user"] = {
        "sub": str(userinfo.get("sub", "")),
        "name": str(userinfo.get("name") or userinfo.get("preferred_username") or "User"),
        "email": str(userinfo.get("email") or userinfo.get("preferred_username") or ""),
    }
    request.session["id_token"] = token.get("id_token", "")
    return RedirectResponse(url="/", status_code=303)


def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


def current_user(request: Request) -> dict[str, Any] | None:
    return request.session.get("user")


def require_user(request: Request) -> dict[str, Any]:
    if not _enabled():
        return {"sub": "local", "name": "Local User", "email": ""}
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
