from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./movie_platform.db"
    secret_key: str = "dev-only-secret"
    admin_password: str = "admin123"
    tmdb_api_key: str = ""
    site_url: str = "http://localhost:8000"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

