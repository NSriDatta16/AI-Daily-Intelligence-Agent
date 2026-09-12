from pathlib import Path

from app.jobs import publish_site


def test_merge_history_keeps_newest_30(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_site, "DATA_DIR", tmp_path)
    existing = [
        {"generated_at": f"2026-09-{day:02d}T09:00:00+00:00", "briefing": "old"}
        for day in range(1, 31)
    ]
    (tmp_path / "briefings.json").write_text(__import__("json").dumps(existing), encoding="utf-8")

    merged = publish_site._merge_history(
        {"generated_at": "2026-10-01T09:00:00+00:00", "briefing": "new"}
    )

    assert len(merged) == 30
    assert merged[0]["generated_at"].startswith("2026-10-01")


def test_merge_articles_deduplicates_by_url(tmp_path, monkeypatch):
    monkeypatch.setattr(publish_site, "DATA_DIR", tmp_path)
    existing = [{"url": "https://example.com/a", "title": "old", "published_at": "2026-09-01"}]
    (tmp_path / "articles.json").write_text(__import__("json").dumps(existing), encoding="utf-8")

    merged = publish_site._merge_articles(
        [
            {"url": "https://example.com/a", "title": "new", "published_at": "2026-09-02"},
            {"url": "https://example.com/b", "title": "second", "published_at": "2026-09-03"},
        ]
    )

    assert len(merged) == 2
    assert merged[0]["url"] == "https://example.com/b"
    assert any(item["title"] == "new" for item in merged)


def test_build_analytics_counts_sources_and_categories():
    analytics = publish_site._build_analytics(
        [
            {"url": "a", "source": "OpenAI", "category": "industry", "title": "OpenAI launches reasoning model", "importance_score": 9, "published_at": "2026-09-12"},
            {"url": "b", "source": "OpenAI", "category": "industry", "title": "OpenAI releases agents", "importance_score": 8, "published_at": "2026-09-11"},
            {"url": "c", "source": "arXiv", "category": "research", "title": "New multimodal benchmark", "importance_score": 7, "published_at": "2026-09-10"},
        ],
        [{"generated_at": "2026-09-12T09:00:00+00:00"}],
    )

    assert analytics["total_articles"] == 3
    assert analytics["total_briefings"] == 1
    assert analytics["sources"][0] == {"source": "OpenAI", "count": 2}
    assert analytics["categories"][0] == {"category": "industry", "count": 2}
