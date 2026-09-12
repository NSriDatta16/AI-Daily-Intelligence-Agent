import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_email(subject: str, body: str, dashboard_url: str | None = None) -> None:
    if not settings.email_enabled:
        return
    if not all([settings.smtp_username, settings.smtp_password, settings.email_from, settings.email_to]):
        raise RuntimeError("Email is enabled but SMTP/email settings are incomplete")

    dashboard_url = dashboard_url or settings.dashboard_url
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = settings.email_to

    email_body = (
        "Good morning — here is your My Daily AI Updates briefing.\n\n"
        f"Dashboard: {dashboard_url}\n\n"
        "Today's briefing:\n\n"
        f"{body}\n"
    )
    message.attach(MIMEText(email_body, "plain", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.email_from, [settings.email_to], message.as_string())
