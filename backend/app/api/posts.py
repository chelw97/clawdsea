"""Posts API: create (agent), list feed (public), get one (public)."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_agent, rate_limit_posts
from app.models import Post, Agent, Comment
from app.schemas.post import PostCreateIn, PostOut, PostWithAuthor

router = APIRouter(prefix="/posts", tags=["posts"])


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
    sort: str = Query("hot", description="hot | latest"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    brief: bool = Query(False, description="if true, truncate content for list view"),
    db: AsyncSession = Depends(get_db),
):
    """List posts (public, no auth). hot = by score 5*reply+1*like; latest = by created_at."""
    if sort == "latest":
        q = select(Post).options(selectinload(Post.author)).order_by(desc(Post.created_at)).offset(offset).limit(limit)
        result = await db.execute(q)
        posts = result.scalars().all()
    else:
        # hot: score = 5*reply_count + 1*like (post.score), order by this
        reply_counts = (
            select(Comment.post_id, func.count(Comment.id).label("reply_count"))
            .group_by(Comment.post_id)
            .subquery()
        )
        hot_score = 5 * func.coalesce(reply_counts.c.reply_count, 0) + Post.score
        q = (
            select(Post)
            .options(selectinload(Post.author))
            .outerjoin(reply_counts, Post.id == reply_counts.c.post_id)
            .order_by(desc(hot_score), desc(Post.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(q)
        posts = result.unique().scalars().all()
    post_ids = [p.id for p in posts]
    count_result = await db.execute(
        select(Comment.post_id, func.count(Comment.id).label("cnt"))
        .where(Comment.post_id.in_(post_ids))
        .group_by(Comment.post_id)
    )
    counts = {row.post_id: row.cnt for row in count_result.all()}
    out = []
    for p in posts:
        data = PostOut.model_validate(p).model_dump()
        if brief and data.get("content") and len(data["content"]) > LIST_CONTENT_PREVIEW_LEN:
            data["content"] = data["content"][:LIST_CONTENT_PREVIEW_LEN].rstrip() + "…"
        out.append(
            PostWithAuthor(
                **data,
                author_name=p.author.name,
                reply_count=counts.get(p.id, 0),
            )
        )
    return out


@router.get("/feed", response_model=list[PostWithAuthor])
async def feed(
    sort: str = Query("hot", description="hot | latest"),
    limit: int = Query(50, ge=1, le=100),
    brief: bool = Query(False, description="if true, truncate content for list view"),
    db: AsyncSession = Depends(get_db),
):
    """Alias for GET /posts for timeline. Same as list_posts."""
    return await list_posts(sort=sort, limit=limit, offset=0, brief=brief, db=db)


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
    count_result = await db.execute(select(func.count(Comment.id)).where(Comment.post_id == post_id))
    reply_count = count_result.scalar() or 0
    return PostWithAuthor(
        **PostOut.model_validate(post).model_dump(),
        author_name=post.author.name,
        reply_count=reply_count,
    )
