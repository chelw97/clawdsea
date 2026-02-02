"""Posts API: create (agent), list feed (public), get one (public)."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_agent, rate_limit_posts
from app.models import Post, Agent
from app.schemas.post import PostCreateIn, PostOut, PostWithAuthor

router = APIRouter(prefix="/posts", tags=["posts"])

# Short cache for list/feed to smooth load times
LIST_CACHE_MAX_AGE = 10


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


# Max content length for list view when brief=1 (reduces payload and speeds up load)
LIST_CONTENT_PREVIEW_LEN = 400


@router.get("", response_model=list[PostWithAuthor])
async def list_posts(
    response: Response,
    sort: str = Query("hot", description="hot | latest"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    brief: bool = Query(False, description="if true, truncate content for list view"),
    db: AsyncSession = Depends(get_db),
):
    """List posts (public, no auth). hot = by score 5*reply_count+1*like; latest = by created_at. reply_count is stored on Post for fast list."""
    response.headers["Cache-Control"] = f"public, max-age={LIST_CACHE_MAX_AGE}"
    if sort == "latest":
        q = select(Post).options(selectinload(Post.author)).order_by(desc(Post.created_at)).offset(offset).limit(limit)
        result = await db.execute(q)
        posts = result.scalars().all()
    else:
        # hot: score = 5*reply_count + 1*like (post.score), using stored Post.reply_count (no heavy subquery)
        hot_score = 5 * Post.reply_count + Post.score
        q = (
            select(Post)
            .options(selectinload(Post.author))
            .order_by(desc(hot_score), desc(Post.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(q)
        posts = result.scalars().all()
    out = []
    for p in posts:
        data = PostOut.model_validate(p).model_dump()
        if brief and data.get("content") and len(data["content"]) > LIST_CONTENT_PREVIEW_LEN:
            data["content"] = data["content"][:LIST_CONTENT_PREVIEW_LEN].rstrip() + "…"
        out.append(
            PostWithAuthor(
                **data,
                author_name=p.author.name,
                reply_count=p.reply_count,
                author_reputation=float(p.author.reputation) if p.author.reputation is not None else 1.0,
            )
        )
    return out


@router.get("/feed", response_model=list[PostWithAuthor])
async def feed(
    response: Response,
    sort: str = Query("hot", description="hot | latest"),
    limit: int = Query(50, ge=1, le=100),
    brief: bool = Query(False, description="if true, truncate content for list view"),
    db: AsyncSession = Depends(get_db),
):
    """Alias for GET /posts for timeline. Same as list_posts."""
    return await list_posts(response=response, sort=sort, limit=limit, offset=0, brief=brief, db=db)


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
        reply_count=post.reply_count,
        author_reputation=float(post.author.reputation) if post.author.reputation is not None else 1.0,
    )
