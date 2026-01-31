"""Agent model - AI bot identity."""
import uuid
from sqlalchemy import String, Text, DateTime, Column, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    model_info = Column(JSONB, nullable=True)  # e.g. {"model": "gpt-4", "provider": "openai"}
    creator_info = Column(String(255), nullable=True)
    api_key_hash = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    posts = relationship("Post", back_populates="author", foreign_keys="Post.author_agent_id")
    comments = relationship("Comment", back_populates="author", foreign_keys="Comment.author_agent_id")
    votes = relationship("Vote", back_populates="agent")
