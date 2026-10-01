"""Centralized application configuration loaded from environment variables."""
from functools import lru_cache
from typing import Literal, Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    APP_NAME: str = "interview-service"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "interview_db"

    # JWT / Auth contract (must match the Auth Service exactly)
    JWT_SECRET_KEY: str = "change-me"
    JWT_ISSUER: str = "auth-servisi"
    JWT_AUDIENCE: str = "mulakat-hazirlik"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Dev-only token issuing endpoint (POST /dev/token)
    ENABLE_DEV_TOKEN_ENDPOINT: bool = True
    DEV_TOKEN_DEFAULT_SUBJECT: str = "dev-user-id"

    # External services
    PROFILE_SERVICE_URL: str = "http://profile-service:8080"
    PROFILE_SERVICE_TIMEOUT_SECONDS: float = 5.0

    # LLM provider. The key is a secret: set it ONLY via environment / .env.
    # When LLM_API_KEY is empty, an offline stub is used instead.
    LLM_PROVIDER: Literal["anthropic", "openai", "azure_openai"] = "anthropic"
    LLM_API_KEY: Optional[SecretStr] = None
    LLM_MODEL: str = ""  # empty = provider default
    LLM_BASE_URL: str = ""  # empty = provider default
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_TOKENS: int = 2000
    # Required only when LLM_PROVIDER=azure_openai. LLM_MODEL is unused in that
    # case; Azure identifies the model via the deployment name in the URL.
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4.1-mini"
    AZURE_OPENAI_API_VERSION: str = "2024-08-01-preview"

    # Question / interview defaults
    DEFAULT_QUESTION_TIME_LIMIT_SECONDS: int = 120
    DEFAULT_INTERVIEW_QUESTION_COUNT: int = 5
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton for process lifetime)."""
    return Settings()
