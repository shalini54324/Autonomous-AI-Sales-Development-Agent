from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
load_dotenv(APP_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///app/data/sales_agent.db").strip()
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "604800"))
    max_companies_per_run: int = int(os.getenv("MAX_COMPANIES_PER_RUN", "25"))
    force_demo_mode: bool = _bool("FORCE_DEMO_MODE", False)
    app_version: str = "1.1.0"

    @property
    def live_ai_available(self) -> bool:
        return bool(self.openai_api_key) and not self.force_demo_mode

settings = Settings()
