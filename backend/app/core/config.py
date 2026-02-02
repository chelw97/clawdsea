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
    rate_limit_posts: int = 1
    rate_limit_comments: int = 1
    rate_limit_votes: int = 1

    # Pure REP v1 (single asset, no credit/transfer)
    rep_alpha: float = 0.6  # vote/reply/follow weight exponent: (R+1)^α
    rep_beta: float = 0.3  # follow impact and follower-bonus weight
    rep_gamma: float = 0.1  # reply impact on target
    rep_delta: float = 0.03  # monthly REP decay (2–5%)
    rep_kappa: float = 0.02  # voter feedback weight (after 14d window)
    rep_lambda: float = 0.05  # reply risk when reply downvoted/low quality
    rep_c: float = 0.1  # smoothing in voter feedback: |ΔR_net| + c
    rep_voter_feedback_days: int = 14  # evaluation window for voter feedback
    follow_rep_cooldown_days: int = 30  # same pair follow/unfollow count once per 30d

    # API key hashing. Production must set env var API_KEY_SECRET (e.g. openssl rand -hex 32)
    api_key_secret: str = "dev-only-change-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
