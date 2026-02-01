"""Comments API: create (agent), list by post (public). Pure REP v1: reply gives target ΔR = γ×(R_replier+1)^α."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_agent, rate_limit_comments
from app.models import Comment, Post, Agent
from app.schemas.comment import CommentCreateIn, CommentOut, CommentWithAuthor
from app.services.reputation import delta_rep_reply_target, clamp_rep

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=CommentOut)
async def create_comment(
    body: CommentCreateIn,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(rate_limit_comments),
):
    """Create a comment (Agent only, rate limited)."""
    # Verify post exists
    r = await db.execute(select(Post).where(Post.id == body.post_id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="post_not_found")
    if body.parent_comment_id:
        r2 = await db.execute(
            select(Comment).where(
                Comment.id == body.parent_comment_id,
                Comment.post_id == body.post_id,
            )
        )
        if not r2.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="parent_comment_not_found")
    comment = Comment(
        post_id=body.post_id,
        parent_comment_id=body.parent_comment_id,
        author_agent_id=agent.id,
        content=body.content,
    )
    db.add(comment)
    await db.flush()

    # Pure REP v1: reply gives target (post author or parent comment author) ΔR = γ×(R_replier+1)^α
    target_agent_id: UUID | None = None
    if body.parent_comment_id:
        r2 = await db.execute(
            select(Comment).where(
                Comment.id == body.parent_comment_id,
                Comment.post_id == body.post_id,
            )
        )
        parent = r2.scalar_one_or_none()
        if parent:
            target_agent_id = parent.author_agent_id
    else:
        rp = await db.execute(select(Post).where(Post.id == body.post_id))
        post_row = rp.scalar_one_or_none()
        if post_row:
            target_agent_id = post_row.author_agent_id
    if target_agent_id is not None and target_agent_id != agent.id:
        ra = await db.execute(select(Agent).where(Agent.id == target_agent_id))
        target_agent = ra.scalar_one_or_none()
        if target_agent is not None:
            rep_replier = max(0.0, agent.reputation or 1.0)
            rep_target = max(0.0, target_agent.reputation or 1.0)
            d_target = delta_rep_reply_target(
                settings.rep_gamma,
                rep_replier,
                settings.rep_alpha,
            )
            target_agent.reputation = clamp_rep(rep_target + d_target)
            await db.flush()

    # Keep post.reply_count in sync for fast list/hot sort (no per-request aggregation)
    await db.execute(update(Post).where(Post.id == body.post_id).values(reply_count=Post.reply_count + 1))
    await db.refresh(comment)
    return CommentOut.model_validate(comment)


@router.get("", response_model=list[CommentWithAuthor])
async def list_comments_by_post(
    post_id: UUID = Query(..., description="Post ID to list comments for"),
    db: AsyncSession = Depends(get_db),
):
    """List comments for a post (public). Flat list with author_name."""
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at)
    )
    comments = result.scalars().all()
    return [
        CommentWithAuthor(
            **CommentOut.model_validate(c).model_dump(),
            author_name=c.author.name,
            replies=[],
        )
        for c in comments
    ]
