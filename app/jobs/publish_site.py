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
from app.storage.database import init_db, save_articles, save_briefing


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

    site = Path("site")
    site.mkdir(exist_ok=True)
    (site / "briefing.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    subject = f"AI Daily Intelligence — {now.astimezone().strftime('%Y-%m-%d')}"
    if settings.email_enabled:
        send_email(subject, briefing)
    if settings.whatsapp_enabled:
        send_whatsapp(briefing)

    print(f"published articles={len(articles)} email={settings.email_enabled} whatsapp={settings.whatsapp_enabled}")
    return briefing


if __name__ == "__main__":
    run()
