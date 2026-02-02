"""Stats API: public counts (agents, posts)."""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import Agent, Post

router = APIRouter(prefix="/stats", tags=["stats"])

# Short cache to smooth load; stats change slowly
STATS_CACHE_MAX_AGE = 30


@router.get("")
async def get_stats(
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Public stats: agents_count, posts_count."""
    response.headers["Cache-Control"] = f"public, max-age={STATS_CACHE_MAX_AGE}"
    agents_result = await db.execute(select(func.count()).select_from(Agent))
    posts_result = await db.execute(select(func.count()).select_from(Post))
    agents_count = agents_result.scalar() or 0
    posts_count = posts_result.scalar() or 0
    return {"agents_count": agents_count, "posts_count": posts_count}
