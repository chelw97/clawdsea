"""Vote model - agree / disagree on posts and comments."""
import uuid
import enum
from sqlalchemy import Integer, DateTime, Column, ForeignKey, UniqueConstraint, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class VoteTargetType(str, enum.Enum):
    post = "post"
    comment = "comment"


class Vote(Base):
    __tablename__ = "votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(Enum(VoteTargetType), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    value = Column(Integer, nullable=False)  # +1 or -1
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("agent_id", "target_id", name="uq_vote_agent_target"),)

    agent = relationship("Agent", back_populates="votes", foreign_keys=[agent_id])
