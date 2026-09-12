from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.agent.summarizer import BriefingAgent
from app.api.auth import callback, cookie_secure, current_user, enabled, login, logout, require_user, session_secret
from app.core.config import settings
from app.ingestion.rss import collect
from app.pipeline.process import deduplicate, rank
from app.sources.feeds import SOURCES
from app.storage.analytics import dashboard_stats, repeated_topics
from app.storage.database import article_history, init_db, recent_briefings

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "app" / "static"

app = FastAPI(title="AI Daily Intelligence Agent", version="0.5.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret() or "local-development-only-change-me",
    https_only=cookie_secure(),
    same_site="lax",
    session_cookie="ai_daily_session",
    max_age=3600,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
init_db()


@app.get("/", name="root")
def root(request: Request):
    if enabled() and not current_user(request):
        return RedirectResponse(url="/auth/login", status_code=303)
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/auth/login", name="auth_login")
async def auth_login(request: Request):
    return await login(request)


@app.get("/auth/callback", name="auth_callback")
async def auth_callback(request: Request):
    return await callback(request)


@app.get("/auth/logout", name="auth_logout")
def auth_logout(request: Request):
    return logout(request)


@app.get("/api/me")
def me(user: dict = Depends(require_user)) -> dict:
    return user


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "database": "connected", "authentication": enabled()}


@app.get("/preview")
def preview(user: dict = Depends(require_user)) -> dict:
    articles = collect(SOURCES, settings.lookback_hours, settings.max_articles)
    ranked = rank(deduplicate(articles), settings.top_stories)
    return {"count": len(ranked), "articles": [
        {"title": a.title, "source": a.source, "category": a.category, "url": a.url,
         "published_at": a.published_at.isoformat(), "importance_score": a.importance_score}
        for a in ranked
    ]}


@app.get("/history")
def history(limit: int = 7, user: dict = Depends(require_user)) -> dict:
    return {"briefings": recent_briefings(max(1, min(limit, 30)))}


@app.get("/articles")
def articles(limit: int = 50, user: dict = Depends(require_user)) -> dict:
    return {"articles": article_history(max(1, min(limit, 200)))}


@app.get("/analytics")
def analytics(user: dict = Depends(require_user)) -> dict:
    data = dashboard_stats()
    data["repeated_topics"] = repeated_topics()
    return data


@app.get("/briefing")
def briefing(user: dict = Depends(require_user)) -> dict:
    articles = collect(SOURCES, settings.lookback_hours, settings.max_articles)
    ranked = rank(deduplicate(articles), settings.top_stories)
    if not ranked:
        return {"headline": "No major AI updates found", "executive_summary": "No source produced an article within the configured 24-hour window.",
                "article_count": 0, "generated_at": datetime.now(timezone.utc).isoformat(), "stories": []}

    generated = BriefingAgent().generate(ranked)
    return {"headline": "Today's AI intelligence", "executive_summary": generated,
            "article_count": len(ranked), "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "stories": [{"title": a.title, "source": a.source, "category": a.category, "url": a.url,
                         "summary": a.summary or "Open the source for the latest details.",
                         "published_at": a.published_at.isoformat(), "importance_score": a.importance_score}
                        for a in ranked]}
