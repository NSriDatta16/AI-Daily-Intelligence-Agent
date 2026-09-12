from datetime import datetime, timedelta, timezone

from app.models.article import Article
from app.pipeline.process import deduplicate, rank


def article(title: str, url: str, source: str = "Test") -> Article:
    return Article(title, url, source, "research", datetime.now(timezone.utc), "AI research")


def test_deduplicate_by_url():
    items = [article("One", "https://example.com/a"), article("One copy", "https://example.com/a")]
    assert len(deduplicate(items)) == 1


def test_deduplicate_near_identical_titles():
    items = [
        article("OpenAI launches a new reasoning model", "https://a.example.com/1"),
        article("OpenAI launches a new reasoning model!", "https://b.example.com/2"),
    ]
    assert len(deduplicate(items)) == 1


def test_rank_returns_requested_limit():
    items = [article(f"AI model research {i}", f"https://example.com/{i}") for i in range(5)]
    ranked = rank(items, 3)
    assert len(ranked) == 3
    assert all(item.importance_score > 0 for item in ranked)


def test_fresher_story_is_preferred_when_other_signals_match():
    old = article("AI model research", "https://example.com/old")
    old.published_at = datetime.now(timezone.utc) - timedelta(hours=20)
    fresh = article("AI model research", "https://example.com/fresh")
    fresh.published_at = datetime.now(timezone.utc)
    ranked = rank([old, fresh], 2)
    assert ranked[0].url.endswith("fresh")
