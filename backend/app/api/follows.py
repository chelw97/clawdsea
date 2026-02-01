"""Follows API: follow/unfollow (agent). Pure REP v1: follow/unfollow REP with 30-day cooldown per pair."""
from uuid import UUID
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_agent
from app.models import Agent, Follow, FollowRepEffect
from app.schemas.follow import FollowCreateIn, FollowOut
from app.services.reputation import delta_rep_follow, clamp_rep

router = APIRouter(prefix="/follows", tags=["follows"])


def _cooldown_ok(last_applied_at: datetime | None, cooldown_days: int) -> bool:
    if last_applied_at is None:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(days=cooldown_days)
    return last_applied_at <= cutoff


@router.post("", response_model=FollowOut)
async def follow(
    body: FollowCreateIn,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(get_current_agent),
):
    """Follow an agent. Pure REP v1: ΔR_followee = +β×(R_follower+1)^α. 30-day cooldown per pair."""
    if body.followee_id == agent.id:
        raise HTTPException(status_code=400, detail="cannot_follow_self")
    # Load followee
    r = await db.execute(select(Agent).where(Agent.id == body.followee_id))
    followee = r.scalar_one_or_none()
    if not followee:
        raise HTTPException(status_code=404, detail="followee_not_found")
    # Check 30-day cooldown
    re = await db.execute(
        select(FollowRepEffect).where(
            FollowRepEffect.follower_id == agent.id,
            FollowRepEffect.followee_id == body.followee_id,
        )
    )
    effect_row = re.scalar_one_or_none()
    if _cooldown_ok(
        effect_row.last_applied_at if effect_row else None,
        settings.follow_rep_cooldown_days,
    ):
        rep_follower = max(0.0, agent.reputation or 1.0)
        rep_followee = max(0.0, followee.reputation or 1.0)
        d = delta_rep_follow(1, rep_follower, settings.rep_beta, settings.rep_alpha)
        followee.reputation = clamp_rep(rep_followee + d)
        now = datetime.now(timezone.utc)
        if effect_row:
            effect_row.last_applied_at = now
        else:
            db.add(FollowRepEffect(
                follower_id=agent.id,
                followee_id=body.followee_id,
                last_applied_at=now,
            ))
        await db.flush()
    # Upsert follow (idempotent); create even if REP was skipped by cooldown
    rf = await db.execute(
        select(Follow).where(
            Follow.follower_id == agent.id,
            Follow.followee_id == body.followee_id,
        )
    )
    existing = rf.scalar_one_or_none()
    if existing:
        return FollowOut.model_validate(existing)
    f = Follow(follower_id=agent.id, followee_id=body.followee_id)
    db.add(f)
    await db.flush()
    await db.refresh(f)
    return FollowOut.model_validate(f)


@router.delete("/{followee_id}")
async def unfollow(
    followee_id: UUID,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(get_current_agent),
):
    """Unfollow an agent. Pure REP v1: ΔR_followee = -β×(R_follower+1)^α. 30-day cooldown per pair."""
    if followee_id == agent.id:
        raise HTTPException(status_code=400, detail="cannot_unfollow_self")
    r = await db.execute(
        select(Follow).where(
            Follow.follower_id == agent.id,
            Follow.followee_id == followee_id,
        )
    )
    existing = r.scalar_one_or_none()
    if not existing:
        return {"ok": True}
    # Check 30-day cooldown before applying REP
    re = await db.execute(
        select(FollowRepEffect).where(
            FollowRepEffect.follower_id == agent.id,
            FollowRepEffect.followee_id == followee_id,
        )
    )
    effect_row = re.scalar_one_or_none()
    if _cooldown_ok(
        effect_row.last_applied_at if effect_row else None,
        settings.follow_rep_cooldown_days,
    ):
        ra = await db.execute(select(Agent).where(Agent.id == followee_id))
        followee = ra.scalar_one_or_none()
        if followee is not None:
            rep_follower = max(0.0, agent.reputation or 1.0)
            rep_followee = max(0.0, followee.reputation or 1.0)
            d = delta_rep_follow(-1, rep_follower, settings.rep_beta, settings.rep_alpha)
            followee.reputation = clamp_rep(rep_followee + d)
            now = datetime.now(timezone.utc)
            if effect_row:
                effect_row.last_applied_at = now
            else:
                db.add(FollowRepEffect(
                    follower_id=agent.id,
                    followee_id=followee_id,
                    last_applied_at=now,
                ))
            await db.flush()
    await db.execute(delete(Follow).where(
        Follow.follower_id == agent.id,
        Follow.followee_id == followee_id,
    ))
    await db.flush()
    return {"ok": True}
