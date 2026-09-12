import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.models.article import Article


def _path() -> str:
    url = settings.database_url
    if not url.startswith("sqlite:///"):
        raise RuntimeError("Only SQLite is supported by the local persistence layer")
    path = url.replace("sqlite:///", "", 1)
    if path.startswith("./"):
        path = path[2:]
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                published_at TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                importance_score REAL NOT NULL DEFAULT 0,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS briefings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generated_at TEXT NOT NULL,
                lookback_hours INTEGER NOT NULL,
                article_count INTEGER NOT NULL,
                briefing TEXT NOT NULL,
                article_urls TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
            CREATE INDEX IF NOT EXISTS idx_briefings_generated_at ON briefings(generated_at);
            """
        )


def save_articles(articles: list[Article], importance: dict[str, float] | None = None) -> None:
    init_db()
    now = datetime.utcnow().isoformat() + "Z"
    importance = importance or {}
    with connect() as conn:
        for article in articles:
            score = float(importance.get(article.url, 0.0))
            conn.execute(
                """
                INSERT INTO articles
                    (url,title,source,category,published_at,summary,importance_score,first_seen_at,last_seen_at)
                VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title, source=excluded.source, category=excluded.category,
                    published_at=excluded.published_at, summary=excluded.summary,
                    importance_score=excluded.importance_score, last_seen_at=excluded.last_seen_at
                """,
                (article.url, article.title, article.source, article.category,
                 article.published_at.isoformat(), article.summary, score, now, now),
            )


def save_briefing(generated_at: str, lookback_hours: int, briefing: str, articles: list[Article]) -> None:
    init_db()
    urls = json.dumps([a.url for a in articles], ensure_ascii=False)
    with connect() as conn:
        conn.execute(
            "INSERT INTO briefings (generated_at,lookback_hours,article_count,briefing,article_urls) VALUES (?,?,?,?,?)",
            (generated_at, lookback_hours, len(articles), briefing, urls),
        )


def recent_briefings(limit: int = 7) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT id,generated_at,lookback_hours,article_count,briefing FROM briefings ORDER BY generated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def article_history(limit: int = 50) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT title,url,source,category,published_at,summary,importance_score FROM articles ORDER BY published_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
