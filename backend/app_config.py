# backend/app_config.py
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    App settings loaded from environment variables and backend/.env.

    Keep backend/.env OUT of GitHub. Commit backend/.env.example instead.
    """

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str | None = None
    SQLALCHEMY_DATABASE_URL: str | None = None

    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REDIS_URL: str | None = None
    ELASTICSEARCH_URL: str | None = None

    CORS_ORIGINS: str = "*"

    def get_database_url(self) -> str:
        url = self.DATABASE_URL or self.SQLALCHEMY_DATABASE_URL
        if not url:
            raise RuntimeError("DATABASE_URL (or SQLALCHEMY_DATABASE_URL) is not set")
        if url.startswith("postgresql://"):
            return "postgresql+psycopg2://" + url.removeprefix("postgresql://")
        return url

    def cors_origins_list(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if raw in ("", "*"):
            return ["*"]
        return [x.strip() for x in raw.split(",") if x.strip()]


settings = Settings()
