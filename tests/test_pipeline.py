from datetime import datetime, timezone

from app.models.article import Article
from app.pipeline.process import deduplicate, rank


def article(title: str, url: str) -> Article:
    return Article(title, url, "Test", "research", datetime.now(timezone.utc), "AI research")


def test_deduplicate_by_url():
    items = [article("One", "https://example.com/a"), article("One copy", "https://example.com/a")]
    assert len(deduplicate(items)) == 1


def test_rank_returns_requested_limit():
    items = [article(f"AI model research {i}", f"https://example.com/{i}") for i in range(5)]
    assert len(rank(items, 3)) == 3
