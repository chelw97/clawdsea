"""Redis-based sliding window rate limit."""
import time
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


def get_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


async def check_rate_limit(
    key_prefix: str,
    agent_id: str,
    limit: int,
    window_seconds: int = 60,
) -> tuple[bool, Optional[str]]:
    """
    Sliding window: allow limit actions per window_seconds.
    Returns (allowed, error_message).
    """
    r = get_redis()
    key = f"ratelimit:{key_prefix}:{agent_id}"
    now = time.time()
    window_start = now - window_seconds

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, window_seconds + 1)
    results = await pipe.execute()
    count = results[1]

    if count >= limit:
        return False, f"rate_limit_exceeded:{key_prefix}"
    return True, None
