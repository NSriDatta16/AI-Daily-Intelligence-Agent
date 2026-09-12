import json
from datetime import datetime, timezone
from pathlib import Path

from app.agent.summarizer import BriefingAgent
from app.core.config import settings
from app.ingestion.rss import collect
from app.notifications.email import send_email
from app.notifications.whatsapp import send_whatsapp
from app.pipeline.process import deduplicate, rank
from app.sources.feeds import SOURCES
from app.storage.analytics import dashboard_stats, repeated_topics
from app.storage.database import article_history, init_db, recent_briefings, save_articles, save_briefing


def _write_json(site: Path, filename: str, payload: dict | list) -> None:
    (site / filename).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run() -> str:
    init_db()
    articles = collect(SOURCES, settings.lookback_hours, settings.max_articles)
    articles = rank(deduplicate(articles), settings.top_stories)
    if not articles:
        raise RuntimeError("No recent AI articles were collected")

    save_articles(articles, {a.url: a.importance_score for a in articles})
    briefing = BriefingAgent().generate(articles)
    now = datetime.now(timezone.utc)
    generated_at = now.isoformat()
    save_briefing(generated_at, settings.lookback_hours, briefing, articles)

    site = Path("site")
    site.mkdir(exist_ok=True)

    payload = {
        "generated_at": generated_at,
        "lookback_hours": settings.lookback_hours,
        "article_count": len(articles),
        "briefing": briefing,
        "articles": [
            {
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "category": a.category,
                "published_at": a.published_at.isoformat(),
                "importance_score": a.importance_score,
                "summary": a.summary,
            }
            for a in articles
        ],
    }

    stats = dashboard_stats()
    stats["repeated_topics"] = repeated_topics()

    _write_json(site, "briefing.json", payload)
    _write_json(site, "analytics.json", stats)
    _write_json(site, "history.json", {"briefings": recent_briefings(30)})
    _write_json(site, "articles.json", {"articles": article_history(200)})

    subject = f"AI Daily Intelligence — {now.astimezone().strftime('%Y-%m-%d')}"
    if settings.email_enabled:
        send_email(subject, briefing)
    if settings.whatsapp_enabled:
        send_whatsapp(briefing)

    print(f"published articles={len(articles)} briefings={stats['total_briefings']} email={settings.email_enabled} whatsapp={settings.whatsapp_enabled}")
    return briefing


if __name__ == "__main__":
    run()
