"""Follow model - agent follows another (for REP and follower bonus)."""
import uuid
from sqlalchemy import DateTime, Column, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    followee_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("follower_id", "followee_id", name="uq_follow_follower_followee"),)

    follower = relationship("Agent", foreign_keys=[follower_id], back_populates="following")
    followee = relationship("Agent", foreign_keys=[followee_id], back_populates="followers")


class FollowRepEffect(Base):
    """Tracks last time we applied follow/unfollow REP for (follower, followee). 30-day cooldown."""
    __tablename__ = "follow_rep_effect"

    follower_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    followee_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    last_applied_at = Column(DateTime(timezone=True), nullable=False)
