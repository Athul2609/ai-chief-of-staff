from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://chiefofstaff:chiefofstaff@localhost:5432/chiefofstaff"
    database_url_sync: str = "postgresql://chiefofstaff:chiefofstaff@localhost:5432/chiefofstaff"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    ollama_embed_model: str = "nomic-embed-text"


@lru_cache
def get_settings() -> Settings:
    return Settings()
