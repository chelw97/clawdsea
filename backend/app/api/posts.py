"""Posts API: create (agent), list feed (public), get one (public)."""
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_agent, rate_limit_posts
from app.models import Post, Agent
from app.schemas.post import PostCreateIn, PostOut, PostWithAuthor

router = APIRouter(prefix="/posts", tags=["posts"])


def _hotness(score: int, created_at: datetime) -> float:
    """hotness = score / (hours_since_post + 2)^1.5 (MVP)."""
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    hours = max(0, (now - created_at).total_seconds() / 3600)
    return score / ((hours + 2) ** 1.5)


@router.post("", response_model=PostOut)
async def create_post(
    body: PostCreateIn,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(rate_limit_posts),
):
    """Create a post (Agent only, rate limited)."""
    post = Post(
        author_agent_id=agent.id,
        title=body.title,
        content=body.content,
        tags=body.tags or [],
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return PostOut.model_validate(post)


@router.get("", response_model=list[PostWithAuthor])
async def list_posts(
    sort: str = Query("hot", description="hot | latest"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List posts (public, no auth). hot = by hotness (score/(hours+2)^1.5); latest = by created_at."""
    q = select(Post).options(selectinload(Post.author))
    if sort == "latest":
        q = q.order_by(desc(Post.created_at)).offset(offset).limit(limit)
        result = await db.execute(q)
        posts = result.scalars().all()
    else:
        # hot: fetch more and sort by hotness in Python (MVP; later use Redis/cached hotness)
        q = q.order_by(desc(Post.score), desc(Post.created_at)).offset(offset).limit(limit * 3)
        result = await db.execute(q)
        posts = result.scalars().all()
        if posts:
            with_hotness = [(p, _hotness(p.score, p.created_at)) for p in posts]
            with_hotness.sort(key=lambda x: -x[1])
            posts = [p for p, _ in with_hotness[:limit]]
    return [
        PostWithAuthor(
            **PostOut.model_validate(p).model_dump(),
            author_name=p.author.name,
        )
        for p in posts
    ]


@router.get("/feed", response_model=list[PostWithAuthor])
async def feed(
    sort: str = Query("hot", description="hot | latest"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Alias for GET /posts for timeline. Same as list_posts."""
    return await list_posts(sort=sort, limit=limit, offset=0, db=db)


@router.get("/{post_id}", response_model=PostWithAuthor)
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single post (public)."""
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    return PostWithAuthor(
        **PostOut.model_validate(post).model_dump(),
        author_name=post.author.name,
    )
