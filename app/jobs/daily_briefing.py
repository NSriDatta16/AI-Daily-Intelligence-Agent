from datetime import datetime, timezone

from app.agent.summarizer import BriefingAgent
from app.core.config import settings
from app.ingestion.rss import collect
from app.notifications.email import send_email
from app.notifications.whatsapp import send_whatsapp
from app.pipeline.process import deduplicate, rank
from app.sources.feeds import SOURCES


def run() -> str:
    articles = collect(SOURCES, settings.lookback_hours, settings.max_articles)
    articles = rank(deduplicate(articles), settings.top_stories)
    if not articles:
        raise RuntimeError("No recent AI articles were collected")

    briefing = BriefingAgent().generate(articles)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"My Daily AI Updates — {timestamp}"

    if settings.email_enabled:
        send_email(subject, briefing, settings.dashboard_url)
    if settings.whatsapp_enabled:
        send_whatsapp(briefing)

    print(
        f"briefing_complete articles={len(articles)} "
        f"email={settings.email_enabled} whatsapp={settings.whatsapp_enabled} "
        f"dashboard={settings.dashboard_url}"
    )
    return briefing


if __name__ == "__main__":
    print(run())
