from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    app_name: str = Field(default="Yamaha Advisor API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_url: str = Field(default="https://api.openai.com/v1/chat/completions", alias="OPENAI_URL")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.2, alias="OPENAI_TEMPERATURE")
    openai_timeout: int = Field(default=30, alias="OPENAI_TIMEOUT")
    openai_max_tokens: int = Field(default=1000, alias="OPENAI_MAX_TOKENS")


@lru_cache()
def get_settings() -> "Settings":
    """Return a cached settings instance for dependency injection."""

    return Settings()


settings = get_settings()
