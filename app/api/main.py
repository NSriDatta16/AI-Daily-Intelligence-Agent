from fastapi import FastAPI

from app.core.config import settings
from app.ingestion.rss import collect
from app.pipeline.process import deduplicate, rank
from app.sources.feeds import SOURCES

app = FastAPI(title="AI Daily Intelligence Agent", version="0.1.0")


@app.get("/")
def root() -> dict:
    return {
        "service": "AI Daily Intelligence Agent",
        "status": "running",
        "endpoints": ["/health", "/preview"],
    }


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
            {"title": a.title, "source": a.source, "category": a.category, "url": a.url}
            for a in ranked
        ],
    }
