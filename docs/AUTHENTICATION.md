# Production authentication

The dashboard now has a real OpenID Connect authentication layer for Microsoft Entra ID. The implementation uses Authlib's Starlette integration and a signed server-side session cookie. Entra handles user authentication; the application does not store user passwords.

Microsoft documents OIDC as the identity layer built on OAuth 2.0, and recommends the authorization-code flow for modern web applications. Authlib supports the same Starlette/FastAPI pattern with an OIDC discovery URL. See:

- https://learn.microsoft.com/en-us/entra/architecture/auth-oidc
- https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow
- https://docs.authlib.org/en/latest/client/frameworks.html

## Current implementation

When `AUTH_ENABLED=true`:

1. `/` redirects unauthenticated users to `/auth/login`.
2. `/auth/login` redirects to Microsoft Entra ID.
3. `/auth/callback` validates the OIDC response and stores only minimal identity claims in the signed session.
4. `/api/me` exposes the authenticated identity to the UI.
5. `/preview`, `/history`, `/articles`, `/analytics`, and `/briefing` require an authenticated session.
6. `/auth/logout` clears the application session.
7. `AUTH_ALLOWED_EMAILS` can restrict access to an explicit comma-separated allowlist.

The session is HTTP-only through Starlette's `SessionMiddleware`, uses `SameSite=Lax`, and is HTTPS-only when `AUTH_COOKIE_SECURE=true`.

## Required production environment variables

```text
AUTH_ENABLED=true
AUTH_SESSION_SECRET=<long-random-secret>
ENTRA_TENANT_ID=<tenant-id>
ENTRA_CLIENT_ID=<app-registration-client-id>
ENTRA_CLIENT_SECRET=<client-secret>
AUTH_REDIRECT_URI=https://<backend-domain>/auth/callback
AUTH_ALLOWED_EMAILS=<comma-separated-allowed-emails>
AUTH_COOKIE_SECURE=true
```

## Microsoft Entra app registration

Create an App Registration in Microsoft Entra ID and add a **Web** redirect URI matching `AUTH_REDIRECT_URI` exactly.

For a single-user/private dashboard, keep the application single-tenant and set `AUTH_ALLOWED_EMAILS` to the intended account(s). Do not put the client secret in the repository or frontend JavaScript.

## Hosting requirement

GitHub Pages remains the existing static/public dashboard. GitHub documents Pages as static hosting and warns that Pages sites are publicly available. Therefore, the new authentication layer must be served by the FastAPI application on a server such as Azure Container Apps; a client-side JavaScript login gate on GitHub Pages would not protect the underlying JSON data.

The intended production flow is:

```text
Browser
  |
  v
Azure Container Apps / FastAPI
  |
  +--> Microsoft Entra ID (OIDC)
  |
  +--> authenticated dashboard/API
  |
  +--> persistent database
  |
  +--> Gemini / RSS ingestion
  |
  +--> daily notification workflow
```

Do not enable `AUTH_ENABLED=true` on the current GitHub Pages deployment. First deploy the FastAPI application to a real backend and move protected dashboard data behind the authenticated API.
