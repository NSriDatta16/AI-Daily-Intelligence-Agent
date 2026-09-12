from __future__ import annotations

from typing import Any

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from app.core.config import settings


oauth = OAuth()


def _configured() -> bool:
    return all(
        [
            settings.auth_enabled,
            settings.entra_tenant_id,
            settings.entra_client_id,
            settings.entra_client_secret,
            settings.auth_session_secret,
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
        client_id=settings.entra_client_id,
        client_secret=settings.entra_client_secret,
        server_metadata_url=(
            f"https://login.microsoftonline.com/{settings.entra_tenant_id}"
            "/v2.0/.well-known/openid-configuration"
        ),
        client_kwargs={"scope": "openid profile email"},
    )


def _allowed(user: dict[str, Any]) -> bool:
    allowed = {
        value.strip().lower()
        for value in settings.auth_allowed_emails.split(",")
        if value.strip()
    }
    if not allowed:
        return True
    email = str(user.get("email") or user.get("preferred_username") or "").lower()
    return email in allowed


async def login(request: Request) -> RedirectResponse:
    client = _client()
    redirect_uri = settings.auth_redirect_uri or str(request.url_for("auth_callback"))
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
    if not settings.auth_enabled:
        return {"sub": "local", "name": "Local User", "email": ""}
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
