"""Debug Dojo backend configuration loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings sourced from environment / .env file."""

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./debug_dojo.db"

    # Judge0 Direct CE
    judge0_base_url: str = "https://ce.judge0.com"
    judge0_api_key: str = ""
    judge0_language_id: Optional[int] = None
    judge0_request_timeout: float = 10.0
    judge0_execution_timeout: float = 5.0
    judge0_poll_interval: float = 1.0
    judge0_max_poll_time: float = 30.0

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # App
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    app_env: str = "development"

    # Render supplies PORT
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
