from app.core.config import settings


def send_whatsapp(body: str) -> None:
    if not settings.whatsapp_enabled:
        return
    if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_whatsapp_from, settings.whatsapp_to]):
        raise RuntimeError("WhatsApp is enabled but Twilio settings are incomplete")
    from twilio.rest import Client

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    client.messages.create(
        from_=settings.twilio_whatsapp_from,
        to=settings.whatsapp_to,
        body=body,
    )
