import hashlib
import re
from collections import Counter

from app.models.article import Article

AI_TERMS = {
    "artificial intelligence", "ai", "llm", "language model", "generative ai",
    "agent", "agents", "machine learning", "deep learning", "transformer",
    "multimodal", "computer vision", "reasoning", "inference", "open source",
    "robotics", "foundation model", "embedding", "rag", "research", "gpu",
}


def content_hash(article: Article) -> str:
    raw = f"{article.title}|{article.url}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def deduplicate(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    result: list[Article] = []
    for article in articles:
        key = article.key or content_hash(article)
        if key in seen:
            continue
        seen.add(key)
        result.append(article)
    return result


def _score(article: Article) -> float:
    text = re.sub(r"[^a-z0-9 ]", " ", f"{article.title} {article.summary}".lower())
    tokens = Counter(text.split())
    relevance = sum(tokens[t] for t in AI_TERMS)
    source_bonus = {"OpenAI": 3, "Google AI": 3, "Microsoft Research": 2.5, "Meta AI": 2.5, "NVIDIA AI": 2}.get(article.source, 1)
    return relevance + source_bonus


def rank(articles: list[Article], limit: int) -> list[Article]:
    return sorted(articles, key=_score, reverse=True)[:limit]
