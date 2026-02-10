from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Salesforce OAuth
    sf_client_id: str = ""
    sf_client_secret: str = ""
    sf_redirect_uri: str = "http://localhost:8000/auth/callback"
    sf_login_url: str = "https://login.salesforce.com"

    # App
    secret_key: str = "change-me-in-production"
    frontend_url: str = "http://localhost:5173"
    debug: bool = True

    model_config = {"env_file": ".env"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
