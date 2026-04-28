from functools import lru_cache
from pydantic import AnyHttpUrl, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinMate UZ API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://finmate:finmate@localhost:5432/finmate"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = Field(default="change-me-local-dev-secret", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    cors_origins: list[AnyHttpUrl] | list[str] = ["http://localhost:3000"]
    default_currency: str = "UZS"
    bot_api_token: str = Field(default="local-bot-token", min_length=8)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment.lower() != "production":
            return self
        weak_values = {
            "change-me-local-dev-secret",
            "change-me-local-dev-secret-for-local-only",
            "local-bot-token",
            "local-bot-token-for-local-only",
        }
        if self.jwt_secret_key in weak_values or self.jwt_secret_key.startswith("replace-with") or len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be a strong production secret")
        if self.bot_api_token in weak_values or self.bot_api_token.startswith("replace-with") or len(self.bot_api_token) < 24:
            raise ValueError("BOT_API_TOKEN must be a strong production secret")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
