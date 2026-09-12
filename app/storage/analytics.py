from collections import Counter
from datetime import datetime, timezone

from app.storage.database import connect, init_db


def dashboard_stats() -> dict:
    init_db()
    with connect() as conn:
        total_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        total_briefings = conn.execute("SELECT COUNT(*) FROM briefings").fetchone()[0]
        sources = conn.execute("SELECT source, COUNT(*) AS count FROM articles GROUP BY source ORDER BY count DESC").fetchall()
        categories = conn.execute("SELECT category, COUNT(*) AS count FROM articles GROUP BY category ORDER BY count DESC").fetchall()
        top = conn.execute("SELECT title,url,source,category,published_at,importance_score FROM articles ORDER BY importance_score DESC,published_at DESC LIMIT 10").fetchall()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": total_articles,
        "total_briefings": total_briefings,
        "sources": [dict(r) for r in sources],
        "categories": [dict(r) for r in categories],
        "top_articles": [dict(r) for r in top],
    }


def repeated_topics(limit: int = 10) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute("SELECT title, source, published_at FROM articles ORDER BY published_at DESC LIMIT 500").fetchall()
    tokens = Counter()
    for row in rows:
        words = {w for w in row[0].lower().replace('-', ' ').split() if len(w) >= 5}
        tokens.update(words)
    stop = {'about','after','could','their','there','which','these','using','with','from','model','models','artificial','intelligence'}
    return [{"topic": word, "mentions": count} for word, count in tokens.most_common() if word not in stop][:limit]
