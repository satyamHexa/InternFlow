from __future__ import annotations

from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_JWT_SECRET = "change_me_to_at_least_32_characters_long_secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "InternFlow"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DB_ECHO: bool = False

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/internflow"
    )

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ──────────────────────────────────────────────────────
    JWT_SECRET: str = _DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ─────────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── Rate Limiting ────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    # ── Azure OpenAI ─────────────────────────────────────────────
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"

    # ── Azure Storage ────────────────────────────────────────────
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_RESUMES: str = "resumes"
    AZURE_STORAGE_CONTAINER_DOCUMENTS: str = "documents"
    AZURE_STORAGE_CONTAINER_CERTIFICATES: str = "certificates"

    # ── Azure Document Intelligence ──────────────────────────────
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str = ""
    AZURE_DOCUMENT_INTELLIGENCE_KEY: str = ""

    # ── Email ────────────────────────────────────────────────────
    EMAIL_SERVICE_PROVIDER: str = "sendgrid"
    EMAIL_SERVICE_API_KEY: str = ""
    EMAIL_FROM_ADDRESS: str = "noreply@internflow.com"
    EMAIL_FROM_NAME: str = "Intern Flow"

    # ── Teams ────────────────────────────────────────────────────
    TEAMS_WEBHOOK_URL: str = ""

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def ensure_async_driver(cls, v: str) -> str:
        """Ensure the database URL uses the asyncpg driver."""
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Prevent startup with insecure defaults in production."""
        if self.APP_ENV == "production":
            if self.JWT_SECRET == _DEFAULT_JWT_SECRET:
                raise ValueError(
                    "JWT_SECRET must be changed from the default value in production. "
                    "Set a strong secret of at least 32 characters in your .env file."
                )
            if len(self.JWT_SECRET) < 32:
                raise ValueError("JWT_SECRET must be at least 32 characters long.")
        return self

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
