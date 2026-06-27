"""Application settings.

Secrets (DB credentials) come from environment variables / .env — never
hardcoded (SECURITY-12). The .env file is gitignored and injected on the host.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MINIAIP_", extra="ignore")

    # e.g. postgresql://user:pass@host:5432/mini_aip?sslmode=require
    database_url: str = "postgresql://localhost:5432/mini_aip"
