import json

from openai import OpenAI

from app.core.config import settings
from app.models.article import Article


class BriefingAgent:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for briefing generation")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, articles: list[Article]) -> str:
        payload = [
            {
                "title": a.title,
                "source": a.source,
                "category": a.category,
                "url": a.url,
                "published_at": a.published_at.isoformat(),
                "excerpt": a.summary[:1500],
            }
            for a in articles
        ]
        prompt = (
            "Create a concise daily AI intelligence briefing from the supplied articles. "
            "Prioritize genuinely important developments over promotional noise. "
            "For each story give: headline, what happened, why it matters, and source link. "
            "Then include Research, Open Source, Industry, and What To Watch sections when relevant. "
            "Do not invent facts. Use only supplied information.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        )
        response = self.client.responses.create(
            model=settings.openai_model,
            input=prompt,
        )
        return response.output_text.strip()
