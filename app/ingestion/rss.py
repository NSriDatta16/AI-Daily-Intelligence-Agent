from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser

from app.models.article import Article
from app.sources.feeds import FeedSource


def _published(entry) -> datetime:
    value = entry.get("published") or entry.get("updated")
    if value:
        try:
            dt = parsedate_to_datetime(value)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc)


def fetch_feed(source: FeedSource, lookback_hours: int = 24, limit: int = 20) -> list[Article]:
    parsed = feedparser.parse(source.url)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=lookback_hours)
    articles: list[Article] = []
    for entry in parsed.entries[:limit]:
        url = entry.get("link", "").strip()
        title = entry.get("title", "").strip()
        if not url or not title:
            continue
        published = _published(entry)
        # Some feeds occasionally publish a future timestamp because of
        # timezone/publishing metadata errors. Never include future stories
        # in a real-time lookback window.
        if published > now or published < cutoff:
            continue
        articles.append(
            Article(
                title=title,
                url=url,
                source=source.name,
                category=source.category,
                published_at=published,
                summary=entry.get("summary", ""),
            )
        )
    return articles


def collect(sources: list[FeedSource], lookback_hours: int, max_articles: int) -> list[Article]:
    articles: list[Article] = []
    for source in sources:
        try:
            articles.extend(fetch_feed(source, lookback_hours=lookback_hours))
        except Exception as exc:
            print(f"feed_error source={source.name!r} error={exc}")
    return articles[:max_articles]
