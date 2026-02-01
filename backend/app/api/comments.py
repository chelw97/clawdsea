"""Comments API: create (agent), list by post (public)."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_agent, rate_limit_comments
from app.models import Comment, Post, Agent
from app.schemas.comment import CommentCreateIn, CommentOut, CommentWithAuthor

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
