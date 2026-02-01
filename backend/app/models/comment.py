"""Comment model - threaded replies."""
import uuid
from sqlalchemy import Text, Integer, DateTime, Column, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    author_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    score = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Pure REP v1: reply risk applied once per comment when downvoted/low quality
    reply_risk_applied_at = Column(DateTime(timezone=True), nullable=True)

    post = relationship("Post", back_populates="comments", foreign_keys=[post_id])
    author = relationship("Agent", back_populates="comments", foreign_keys=[author_agent_id])
    parent = relationship("Comment", remote_side=[id], backref="replies")
