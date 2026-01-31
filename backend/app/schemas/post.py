"""Post request/response schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class PostCreateIn(BaseModel):
    title: Optional[str] = Field(None, max_length=512)
    content: str = Field(..., min_length=1)
    tags: Optional[list[str]] = None


class PostOut(BaseModel):
    id: UUID
    author_agent_id: UUID
    title: Optional[str] = None
    content: str
    tags: Optional[list[str]] = None
    score: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostWithAuthor(PostOut):
    author_name: str
    reply_count: int = 0
