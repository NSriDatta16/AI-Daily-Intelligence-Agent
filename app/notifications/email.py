import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_email(subject: str, body: str) -> None:
    if not settings.email_enabled:
        return
    if not all([settings.smtp_username, settings.smtp_password, settings.email_from, settings.email_to]):
        raise RuntimeError("Email is enabled but SMTP/email settings are incomplete")
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = settings.email_to
    message.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.email_from, [settings.email_to], message.as_string())
