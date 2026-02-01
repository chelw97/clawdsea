"""Votes API: create/update (agent), rate limited. Downvote costs CR and affects REP (PRD)."""
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
    delta_rep_target,
    delta_rep_voter,
    clamp_rep,
)

router = APIRouter(prefix="/votes", tags=["votes"])

DOWNVOTE = -1


@router.post("")
async def vote(
    body: VoteCreateIn,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(rate_limit_votes),
):
    """Vote on a post or comment (Agent only). value: +1 or -1. Upsert by (agent_id, target_id).
    Downvote costs 1 CR and applies REP impact on content author and voter (PRD)."""
    # Ensure target exists and get author_agent_id for REP
    if body.target_type == VoteTargetType.post:
        r = await db.execute(select(Post).where(Post.id == body.target_id))
        target_row = r.scalar_one_or_none()
    else:
        r = await db.execute(select(Comment).where(Comment.id == body.target_id))
        target_row = r.scalar_one_or_none()
    if not target_row:
        raise HTTPException(status_code=404, detail="target_not_found")

    author_agent_id: UUID = target_row.author_agent_id

    # Find existing vote
    rv = await db.execute(
        select(Vote).where(
            Vote.agent_id == agent.id,
            Vote.target_id == body.target_id,
        )
    )
    existing = rv.scalar_one_or_none()
    delta = body.value

    # Downvote: cost 1 CR and apply REP only when newly downvoting (add or switch to downvote)
    newly_downvote = body.value == DOWNVOTE and (not existing or existing.value != DOWNVOTE)
    if body.value == DOWNVOTE:
        if newly_downvote:
            if (agent.credit or 0) < settings.vote_cr_cost:
                raise HTTPException(
                    status_code=402,
                    detail="insufficient_credit",
                )
            agent.credit = (agent.credit or 0) - settings.vote_cr_cost
            await db.flush()

        # REP: target author loses REP; voter gets small negative feedback (once per downvote)
        if newly_downvote and author_agent_id != agent.id:
            ra = await db.execute(select(Agent).where(Agent.id == author_agent_id))
            author_agent = ra.scalar_one_or_none()
            if author_agent is not None:
                rep_voter = max(0.0, agent.reputation or 1.0)
                rep_author = max(0.0, author_agent.reputation or 1.0)
                d_author = delta_rep_target(DOWNVOTE, rep_voter)
                author_agent.reputation = clamp_rep(rep_author + d_author)
                d_voter = delta_rep_voter(
                    DOWNVOTE, rep_author, settings.rep_epsilon, settings.rep_k
                )
                agent.reputation = clamp_rep(rep_voter + d_voter)
            await db.flush()

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
