"""Comment request/response schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class CommentCreateIn(BaseModel):
    post_id: UUID
    parent_comment_id: Optional[UUID] = None
    content: str = Field(..., min_length=1)


class CommentOut(BaseModel):
    id: UUID
    post_id: UUID
    parent_comment_id: Optional[UUID] = None
    author_agent_id: UUID
    content: str
    score: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentWithAuthor(CommentOut):
    author_name: str
    replies: list["CommentWithAuthor"] = []


CommentWithAuthor.model_rebuild()
