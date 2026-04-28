from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LocalGPT Homework"
    app_env: str = "local"
    secret_key: str = "change-me-to-a-long-random-string"
    access_token_expire_minutes: int = 30
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/homework_chat"
    redis_url: str = "redis://localhost:6379/0"
    refresh_ttl_days: int = 30
    github_client_id: str = ""
    github_client_secret: str = ""
    github_callback_url: str = "http://localhost:8000/auth/github/callback"
    llm_model_path: str = "model.gguf"
    llm_max_tokens: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
