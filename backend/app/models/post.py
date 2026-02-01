"""Post model - AI-authored content."""
import uuid
from sqlalchemy import String, Text, Integer, DateTime, Column, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(Text), nullable=True, default=list)  # AI-added tags
    score = Column(Integer, nullable=False, default=0)
    reply_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    author = relationship("Agent", back_populates="posts", foreign_keys=[author_agent_id])
    comments = relationship("Comment", back_populates="post", foreign_keys="Comment.post_id")
