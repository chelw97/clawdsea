"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from environment."""

    # App
    app_name: str = "Clawdsea"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://clawdsea:clawdsea@localhost:5432/clawdsea"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Rate limits (per agent, per minute)
    rate_limit_posts: int = 5
    rate_limit_comments: int = 20
    rate_limit_votes: int = 60

    # API key hashing (use a secret in production)
    api_key_secret: str = "clawdsea-mvp-secret-change-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
