import json
from collections import Counter
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

DATA_DIR = Path("data")
SITE_DIR = Path("site")


def _write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path, default: dict | list) -> dict | list:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _article_payload(article) -> dict:
    return {
        "title": article.title,
        "url": article.url,
        "source": article.source,
        "category": article.category,
        "published_at": article.published_at.isoformat(),
        "importance_score": article.importance_score,
        "summary": article.summary,
    }


def _merge_history(current: dict) -> list[dict]:
    existing = _read_json(DATA_DIR / "briefings.json", [])
    if not isinstance(existing, list):
        existing = []
    merged = [current, *existing]
    seen: set[str] = set()
    result: list[dict] = []
    for item in merged:
        key = str(item.get("generated_at", ""))
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result[:30]


def _merge_articles(current: list[dict]) -> list[dict]:
    existing = _read_json(DATA_DIR / "articles.json", [])
    if not isinstance(existing, list):
        existing = []
    by_url: dict[str, dict] = {}
    for item in [*existing, *current]:
        url = str(item.get("url", "")).strip().lower()
        if url:
            by_url[url] = item
    result = list(by_url.values())
    result.sort(key=lambda item: str(item.get("published_at", "")), reverse=True)
    return result[:500]


def _build_analytics(articles: list[dict], briefings: list[dict]) -> dict:
    source_counts = Counter(str(a.get("source", "Unknown")) for a in articles)
    category_counts = Counter(str(a.get("category", "Unknown")) for a in articles)
    words = Counter()
    stop = {
        "about", "after", "could", "their", "there", "which", "these", "using",
        "with", "from", "model", "models", "artificial", "intelligence", "latest",
        "announces", "announced", "research", "technology",
    }
    for article in articles:
        tokens = {
            token.strip(".,:;!?()[]{}\"'").lower()
            for token in str(article.get("title", "")).replace("-", " ").split()
        }
        words.update(word for word in tokens if len(word) >= 5 and word not in stop)
    top_articles = sorted(
        articles,
        key=lambda item: (float(item.get("importance_score", 0)), str(item.get("published_at", ""))),
        reverse=True,
    )[:10]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(articles),
        "total_briefings": len(briefings),
        "sources": [{"source": k, "count": v} for k, v in source_counts.most_common()],
        "categories": [{"category": k, "count": v} for k, v in category_counts.most_common()],
        "top_articles": top_articles,
        "repeated_topics": [{"topic": k, "mentions": v} for k, v in words.most_common(15)],
    }


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

    current_articles = [_article_payload(a) for a in articles]
    current_briefing = {
        "generated_at": generated_at,
        "lookback_hours": settings.lookback_hours,
        "article_count": len(articles),
        "briefing": briefing,
        "articles": current_articles,
    }
    save_briefing(generated_at, settings.lookback_hours, briefing, articles)

    # GitHub-hosted JSON is the durable history because Actions runners are ephemeral.
    briefings = _merge_history(current_briefing)
    all_articles = _merge_articles(current_articles)
    analytics = _build_analytics(all_articles, briefings)
    _write_json(DATA_DIR / "briefings.json", briefings)
    _write_json(DATA_DIR / "articles.json", all_articles)
    _write_json(DATA_DIR / "analytics.json", analytics)

    SITE_DIR.mkdir(exist_ok=True)
    _write_json(SITE_DIR / "briefing.json", current_briefing)
    _write_json(SITE_DIR / "analytics.json", analytics)
    _write_json(SITE_DIR / "history.json", {"briefings": briefings})
    _write_json(SITE_DIR / "articles.json", {"articles": all_articles})

    subject = f"AI Daily Intelligence — {now.astimezone().strftime('%Y-%m-%d')}"
    if settings.email_enabled:
        send_email(subject, briefing)
    if settings.whatsapp_enabled:
        send_whatsapp(briefing)

    print(
        f"published articles={len(articles)} stored_articles={len(all_articles)} "
        f"briefings={len(briefings)} email={settings.email_enabled} whatsapp={settings.whatsapp_enabled}"
    )
    return briefing


if __name__ == "__main__":
    run()
