from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    title: str
    url: str
    source: str
    category: str
    published_at: datetime
    summary: str = ""
    content: str = ""
    importance_score: float = 0.0

    @property
    def key(self) -> str:
        return self.url.strip().lower()
