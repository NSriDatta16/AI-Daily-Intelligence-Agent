from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agent.summarizer import BriefingAgent
from app.core.config import settings
from app.ingestion.rss import collect
from app.pipeline.process import deduplicate, rank
from app.sources.feeds import SOURCES

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "app" / "static"

app = FastAPI(title="AI Daily Intelligence Agent", version="0.2.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.get("/preview")
def preview() -> dict:
    articles = collect(SOURCES, settings.lookback_hours, settings.max_articles)
    ranked = rank(deduplicate(articles), settings.top_stories)
    return {
        "count": len(ranked),
        "articles": [
            {
                "title": a.title,
                "source": a.source,
                "category": a.category,
                "url": a.url,
                "published_at": a.published_at.isoformat(),
            }
            for a in ranked
        ],
    }


@app.get("/briefing")
def briefing() -> dict:
    articles = collect(SOURCES, settings.lookback_hours, settings.max_articles)
    ranked = rank(deduplicate(articles), settings.top_stories)
    if not ranked:
        return {
            "headline": "No major AI updates found",
            "executive_summary": "No source produced an article within the configured 24-hour window.",
            "article_count": 0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "stories": [],
        }

    generated = BriefingAgent().generate(ranked)
    return {
        "headline": "Today's AI intelligence",
        "executive_summary": generated,
        "article_count": len(ranked),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "stories": [
            {
                "title": a.title,
                "source": a.source,
                "category": a.category,
                "url": a.url,
                "summary": a.summary or "Open the source for the latest details.",
                "published_at": a.published_at.isoformat(),
            }
            for a in ranked
        ],
    }
