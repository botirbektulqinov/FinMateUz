from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    environment: str = "local"
    telegram_bot_token: str = "dev-token"
    api_base_url: str = "http://api:8000/api/v1"
    bot_api_token: str = "local-bot-token"
    transcriber_provider: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_settings(self) -> "BotSettings":
        if self.environment.lower() != "production":
            return self
        if self.telegram_bot_token == "dev-token" or self.telegram_bot_token.startswith("replace-with") or len(self.telegram_bot_token) < 30:
            raise ValueError("TELEGRAM_BOT_TOKEN must be set in production")
        if (
            self.bot_api_token in {"local-bot-token", "local-bot-token-for-local-only"}
            or self.bot_api_token.startswith("replace-with")
            or len(self.bot_api_token) < 24
        ):
            raise ValueError("BOT_API_TOKEN must be a strong production secret")
        return self


@lru_cache
def get_settings() -> BotSettings:
    return BotSettings()
