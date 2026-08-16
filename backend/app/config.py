"""Application configuration loaded from environment / .env file."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate the project root .env regardless of the process working directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Service Desk L1 Copilot"
    app_version: str = "1.0.0"

    openrouter_api_key: str = ""
    openrouter_model: str = "deepseek/deepseek-chat-v3-0324"
    openrouter_max_tokens: int = 600
    openrouter_temperature: float = 0.3
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout: float = 60.0

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    kb_dir: str = "kb"
    seed_data_dir: str = "backend/app/data"
    triage_config: str = "backend/config/triage.yaml"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def has_api_key(self) -> bool:
        return bool(self.openrouter_api_key) and self.openrouter_api_key.startswith("sk-or-")


@lru_cache
def get_settings() -> Settings:
    return Settings()
