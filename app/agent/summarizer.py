import json
import time

from google import genai

from app.core.config import settings
from app.models.article import Article


class BriefingAgent:
    RETRYABLE_CODES = {429, 500, 502, 503, 504}
    FALLBACK_MODELS = ("gemini-flash-latest", "gemini-2.5-flash-lite")

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required for briefing generation")
        self.client = genai.Client(api_key=settings.gemini_api_key)

    @classmethod
    def _is_retryable(cls, exc: Exception) -> bool:
        code = getattr(exc, "code", None)
        if isinstance(code, int) and code in cls.RETRYABLE_CODES:
            return True

        name = type(exc).__name__
        return name in {"RateLimitError", "InternalServerError", "ServerError"}

    def _generate_with_model(self, model: str, prompt: str) -> str:
        last_error: Exception | None = None

        # Gemini can temporarily return 429/5xx during quota or capacity spikes.
        # Retry with exponential backoff before switching to a fallback model.
        for attempt in range(4):
            try:
                interaction = self.client.interactions.create(
                    model=model,
                    input=prompt,
                )
                result = (interaction.output_text or "").strip()
                if not result:
                    raise RuntimeError(f"Gemini returned empty output for model {model}")
                return result
            except Exception as exc:
                last_error = exc
                if not self._is_retryable(exc) or attempt == 3:
                    raise
                delay = 2 ** (attempt + 1)
                print(
                    f"WARNING: Gemini model {model} failed with {type(exc).__name__}; "
                    f"retrying in {delay}s (attempt {attempt + 1}/4)"
                )
                time.sleep(delay)

        raise last_error or RuntimeError(f"Gemini generation failed for model {model}")

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

        models = []
        for model in (settings.gemini_model, *self.FALLBACK_MODELS):
            if model and model not in models:
                models.append(model)

        errors: list[str] = []
        for model in models:
            try:
                return self._generate_with_model(model, prompt)
            except Exception as exc:
                errors.append(f"{model}: {type(exc).__name__}: {exc}")
                print(f"WARNING: Gemini model {model} exhausted retries: {exc}")

        raise RuntimeError(
            "All Gemini briefing models failed. " + " | ".join(errors)
        )
