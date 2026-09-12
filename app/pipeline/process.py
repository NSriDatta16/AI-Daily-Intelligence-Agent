import hashlib
import re
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher

from app.models.article import Article
from app.sources.feeds import SOURCES

AI_TERMS = {
    "artificial intelligence", "ai", "llm", "language model", "generative ai",
    "agent", "agents", "machine learning", "deep learning", "transformer",
    "multimodal", "computer vision", "reasoning", "inference", "open source",
    "robotics", "foundation model", "embedding", "rag", "research", "gpu",
}

HIGH_IMPACT_TERMS = {
    "release", "launch", "announces", "introduced", "available", "benchmark",
    "breakthrough", "acquisition", "funding", "partnership", "security", "safety",
    "regulation", "policy", "open weights", "open-source", "model", "agentic",
}

SOURCE_AUTHORITY = {source.name: source.authority for source in SOURCES}


def content_hash(article: Article) -> str:
    raw = f"{article.title}|{article.url}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _normalized_title(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", title.lower()).strip()


def deduplicate(articles: list[Article]) -> list[Article]:
    seen_urls: set[str] = set()
    result: list[Article] = []
    for article in articles:
        key = article.key or content_hash(article)
        if key in seen_urls:
            continue

        title = _normalized_title(article.title)
        if any(SequenceMatcher(None, title, _normalized_title(existing.title)).ratio() >= 0.92 for existing in result):
            continue

        seen_urls.add(key)
        result.append(article)
    return result


def _score(article: Article) -> float:
    text = re.sub(r"[^a-z0-9 ]", " ", f"{article.title} {article.summary}".lower())
    tokens = Counter(text.split())
    relevance = sum(tokens[t] for t in AI_TERMS)
    impact = sum(tokens[t] for t in HIGH_IMPACT_TERMS) * 1.75
    authority = SOURCE_AUTHORITY.get(article.source, 0.60) * 5

    published = article.published_at
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    age_hours = max(0.0, (datetime.now(timezone.utc) - published.astimezone(timezone.utc)).total_seconds() / 3600)
    freshness = max(0.0, 4.0 - (age_hours / 8.0))

    return round(relevance + impact + authority + freshness, 3)


def rank(articles: list[Article], limit: int) -> list[Article]:
    for article in articles:
        article.importance_score = _score(article)

    ranked = sorted(articles, key=lambda item: item.importance_score, reverse=True)

    # Prefer a broad briefing instead of filling all slots with one publisher.
    selected: list[Article] = []
    source_counts: Counter[str] = Counter()
    for article in ranked:
        if source_counts[article.source] >= 3 and len(ranked) - len(selected) > limit:
            continue
        selected.append(article)
        source_counts[article.source] += 1
        if len(selected) >= limit:
            break
    return selected
