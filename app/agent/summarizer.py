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
                "importance_score": a.importance_score,
                "excerpt": a.summary[:1500],
            }
            for a in articles
        ]
        prompt = (
            "Create a concise, decision-useful daily AI intelligence briefing from the supplied articles. "
            "The articles have already been deduplicated and ranked by freshness, relevance, source authority, "
            "and likely impact. Use that ranking as a signal, but independently judge importance. "
            "Lead with the highest-impact developments, not the most promotional language. "
            "For each major story give: headline, what happened, why it matters, and source link. "
            "Group related developments rather than repeating the same event. "
            "Then include Research, Open Source, Industry, and What To Watch sections when relevant. "
            "Clearly distinguish reported facts from implications. Do not invent facts, numbers, quotes, or events. "
            "Use only the supplied information and preserve source links.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        )
        interaction = self.client.interactions.create(
            model=settings.gemini_model,
            input=prompt,
        )
        return (interaction.output_text or "").strip()
