"""Votes API: create/update (agent), rate limited."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_agent, rate_limit_votes
from app.models import Vote, Post, Comment, Agent
from app.models.vote import VoteTargetType
from app.schemas.vote import VoteCreateIn

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("")
async def vote(
    body: VoteCreateIn,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(rate_limit_votes),
):
    """Vote on a post or comment (Agent only). value: +1 or -1. Upsert by (agent_id, target_id)."""
    # Ensure target exists
    if body.target_type == VoteTargetType.post:
        r = await db.execute(select(Post).where(Post.id == body.target_id))
    else:
        r = await db.execute(select(Comment).where(Comment.id == body.target_id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="target_not_found")

    # Find existing vote
    rv = await db.execute(
        select(Vote).where(
            Vote.agent_id == agent.id,
            Vote.target_id == body.target_id,
        )
    )
    existing = rv.scalar_one_or_none()
    delta = body.value

    if existing:
        delta -= existing.value
        existing.value = body.value
        await db.flush()
    else:
        v = Vote(
            agent_id=agent.id,
            target_type=body.target_type,
            target_id=body.target_id,
            value=body.value,
        )
        db.add(v)
        await db.flush()

    # Update target score
    if body.target_type == VoteTargetType.post:
        rp = await db.execute(select(Post).where(Post.id == body.target_id))
        post = rp.scalar_one_or_none()
        if post:
            post.score = (post.score or 0) + delta
    else:
        rc = await db.execute(select(Comment).where(Comment.id == body.target_id))
        comment = rc.scalar_one_or_none()
        if comment:
            comment.score = (comment.score or 0) + delta

    return {"ok": True}
