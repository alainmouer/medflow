"""Application configuration."""
from __future__ import annotations

import os
from typing import Self

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic settings loaded from environment variables."""

    PROJECT_NAME: str = "MedFlow"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./medflow.db"

    # Security (load from env in production)
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h

    # CORS
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "http://localhost:3000")

    # AI / LLM Provider settings
    AI_PROVIDER_PRIORITY: str = os.environ.get("AI_PROVIDER_PRIORITY", "mock")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    MISTRAL_API_KEY: str = os.environ.get("MISTRAL_API_KEY", "")

    # Redis (optional in dev — queue/cache can degrade gracefully)
    REDIS_URL: str = os.environ.get("REDIS_URL", "")

    @property
    def cors_origins_list(self: Self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
