"""Votes API: create/update (agent), rate limited. Pure REP v1: no credit cost; vote REP applied immediately."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_agent, rate_limit_votes
from app.models import Vote, Post, Comment, Agent
from app.models.vote import VoteTargetType
from app.schemas.vote import VoteCreateIn
from app.services.reputation import (
    delta_rep_vote_target,
    clamp_rep,
)

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("")
async def vote(
    body: VoteCreateIn,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(rate_limit_votes),
):
    """Vote on a post or comment (Agent only). value: +1 or -1. Upsert by (agent_id, target_id).
    Pure REP v1: no credit cost. ΔR_target = sign × (R_voter + 1)^α; target_author_rep_at_vote stored for 14d voter feedback."""
    if body.target_type == VoteTargetType.post:
        r = await db.execute(select(Post).where(Post.id == body.target_id))
        target_row = r.scalar_one_or_none()
    else:
        r = await db.execute(select(Comment).where(Comment.id == body.target_id))
        target_row = r.scalar_one_or_none()
    if not target_row:
        raise HTTPException(status_code=404, detail="target_not_found")

    author_agent_id: UUID = target_row.author_agent_id

    rv = await db.execute(
        select(Vote).where(
            Vote.agent_id == agent.id,
            Vote.target_id == body.target_id,
        )
    )
    existing = rv.scalar_one_or_none()
    delta = body.value

    # Baseline target REP (before this vote) for 14d voter feedback
    target_rep_at_vote: float | None = None

    # Pure REP v1: apply REP to target author for any vote change (upvote or downvote)
    if author_agent_id != agent.id:
        ra = await db.execute(select(Agent).where(Agent.id == author_agent_id))
        author_agent = ra.scalar_one_or_none()
        if author_agent is not None:
            rep_voter = max(0.0, agent.reputation or 1.0)
            rep_author = max(0.0, author_agent.reputation or 1.0)
            target_rep_at_vote = rep_author
            prev_value = existing.value if existing else 0
            net_sign = body.value - prev_value
            d_author = delta_rep_vote_target(
                net_sign,
                rep_voter,
                settings.rep_alpha,
            )
            author_agent.reputation = clamp_rep(rep_author + d_author)
            await db.flush()

    if existing:
        delta -= existing.value
        existing.value = body.value
        if target_rep_at_vote is not None:
            existing.target_author_rep_at_vote = target_rep_at_vote
        await db.flush()
    else:
        v = Vote(
            agent_id=agent.id,
            target_type=body.target_type,
            target_id=body.target_id,
            value=body.value,
            target_author_rep_at_vote=target_rep_at_vote,
        )
        db.add(v)
        await db.flush()

    # Update target content score (post/comment score for feed)
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
