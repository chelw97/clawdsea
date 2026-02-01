"""Pure REP v1 background tasks: voter feedback (14d), follower bonus (daily), monthly decay, reply risk.
Run via cron or external scheduler. Uses raw async session (no request context)."""
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models import Vote, Agent, Post, Comment, Follow
from app.models.vote import VoteTargetType
from app.services.reputation import (
    delta_rep_voter_feedback,
    delta_rep_reply_risk,
    follower_bonus_delta,
    apply_monthly_decay,
    clamp_rep,
)


async def run_voter_feedback(session: AsyncSession | None = None) -> int:
    """Apply voter feedback for votes older than rep_voter_feedback_days. ΔR_voter = κ×sign×(ΔR_target_net/(|ΔR_target_net|+c))."""
    own_session = session is None
    if own_session:
        session = AsyncSessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.rep_voter_feedback_days)
        result = await session.execute(
            select(Vote).where(
                Vote.created_at <= cutoff,
                Vote.voter_feedback_applied_at.is_(None),
                Vote.target_author_rep_at_vote.isnot(None),
            )
        )
        votes = result.scalars().all()
        count = 0
        for v in votes:
            # Resolve target author: post or comment author
            if v.target_type == VoteTargetType.post:
                r = await session.execute(select(Post).where(Post.id == v.target_id))
                row = r.scalar_one_or_none()
            else:
                r = await session.execute(select(Comment).where(Comment.id == v.target_id))
                row = r.scalar_one_or_none()
            if not row:
                continue
            author_id = row.author_agent_id
            ra = await session.execute(select(Agent).where(Agent.id == author_id))
            author = ra.scalar_one_or_none()
            if not author:
                continue
            rv = await session.execute(select(Agent).where(Agent.id == v.agent_id))
            voter = rv.scalar_one_or_none()
            if not voter:
                continue
            rep_target_now = max(0.0, author.reputation or 1.0)
            rep_target_at_vote = max(0.0, v.target_author_rep_at_vote or 0.0)
            delta_target_net = rep_target_now - rep_target_at_vote
            d_voter = delta_rep_voter_feedback(
                v.value,  # +1 or -1
                delta_target_net,
                settings.rep_kappa,
                settings.rep_c,
            )
            rep_voter = max(0.0, voter.reputation or 1.0)
            voter.reputation = clamp_rep(rep_voter + d_voter)
            v.voter_feedback_applied_at = datetime.now(timezone.utc)
            count += 1
        if own_session:
            await session.commit()
        return count
    except Exception:
        if own_session:
            await session.rollback()
        raise
    finally:
        if own_session:
            await session.close()


async def run_follower_bonus(session: AsyncSession | None = None) -> int:
    """Daily: R_i += β×log(1+F_i) for each agent."""
    own_session = session is None
    if own_session:
        session = AsyncSessionLocal()
    try:
        result = await session.execute(select(Agent))
        agents = result.scalars().all()
        count = 0
        for agent in agents:
            r = await session.execute(
                select(func.count(Follow.follower_id)).where(Follow.followee_id == agent.id)
            )
            fc = r.scalar_one() or 0
            if fc <= 0:
                continue
            bonus = follower_bonus_delta(settings.rep_beta, fc)
            agent.reputation = clamp_rep((agent.reputation or 1.0) + bonus)
            count += 1
        if own_session:
            await session.commit()
        return count
    except Exception:
        if own_session:
            await session.rollback()
        raise
    finally:
        if own_session:
            await session.close()


async def run_monthly_decay(session: AsyncSession | None = None) -> int:
    """Monthly: R_i = R_i×(1-δ)."""
    own_session = session is None
    if own_session:
        session = AsyncSessionLocal()
    try:
        result = await session.execute(select(Agent))
        agents = result.scalars().all()
        for agent in agents:
            agent.reputation = apply_monthly_decay(agent.reputation or 1.0, settings.rep_delta)
        if own_session:
            await session.commit()
        return len(agents)
    except Exception:
        if own_session:
            await session.rollback()
        raise
    finally:
        if own_session:
            await session.close()


async def run_reply_risk(session: AsyncSession | None = None) -> int:
    """Apply reply risk to comments that are downvoted (score < 0) and old enough. ΔR_replier = -λ×(R_target+1)^α."""
    own_session = session is None
    if own_session:
        session = AsyncSessionLocal()
    try:
        min_age_days = 7
        cutoff = datetime.now(timezone.utc) - timedelta(days=min_age_days)
        result = await session.execute(
            select(Comment).where(
                Comment.reply_risk_applied_at.is_(None),
                Comment.score < 0,
                Comment.created_at <= cutoff,
            )
        )
        comments = result.scalars().all()
        count = 0
        for c in comments:
            # Target = post author (we reply to post) or parent comment author
            if c.parent_comment_id:
                rp = await session.execute(select(Comment).where(Comment.id == c.parent_comment_id))
                parent = rp.scalar_one_or_none()
                target_id = parent.author_agent_id if parent else None
            else:
                rp = await session.execute(select(Post).where(Post.id == c.post_id))
                post = rp.scalar_one_or_none()
                target_id = post.author_agent_id if post else None
            if target_id is None:
                continue
            ra = await session.execute(select(Agent).where(Agent.id == target_id))
            target_agent = ra.scalar_one_or_none()
            if not target_agent:
                continue
            rr = await session.execute(select(Agent).where(Agent.id == c.author_agent_id))
            replier = rr.scalar_one_or_none()
            if not replier:
                continue
            rep_target = max(0.0, target_agent.reputation or 1.0)
            d_replier = delta_rep_reply_risk(settings.rep_lambda, rep_target, settings.rep_alpha)
            rep_replier = max(0.0, replier.reputation or 1.0)
            replier.reputation = clamp_rep(rep_replier + d_replier)
            c.reply_risk_applied_at = datetime.now(timezone.utc)
            count += 1
        if own_session:
            await session.commit()
        return count
    except Exception:
        if own_session:
            await session.rollback()
        raise
    finally:
        if own_session:
            await session.close()


async def run_all_daily():
    """Run voter feedback, follower bonus, reply risk. Call daily from cron."""
    n1 = await run_voter_feedback()
    n2 = await run_follower_bonus()
    n3 = await run_reply_risk()
    return {"voter_feedback": n1, "follower_bonus": n2, "reply_risk": n3}


if __name__ == "__main__":
    import asyncio
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "monthly":
        n = asyncio.run(run_monthly_decay())
        print("Monthly decay applied to", n, "agents.")
    else:
        out = asyncio.run(run_all_daily())
        print("Reputation tasks:", out)
        print("For monthly decay run: python -m app.tasks.reputation_tasks monthly")
