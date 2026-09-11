from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    email_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_to: str = ""

    whatsapp_enabled: bool = False
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    whatsapp_to: str = ""

    database_url: str = "sqlite:///./data/briefing.db"
    lookback_hours: int = 24
    max_articles: int = 60
    top_stories: int = 8

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
