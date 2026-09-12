import json

from google import genai

from app.core.config import settings
from app.models.article import Article


class BriefingAgent:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required for briefing generation")
        self.client = genai.Client(api_key=settings.gemini_api_key)

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
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        return (response.text or "").strip()
