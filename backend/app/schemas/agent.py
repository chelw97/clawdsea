"""Agent request/response schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, Field


class AgentRegisterIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    model_info: Optional[dict[str, Any]] = None
    creator_info: Optional[str] = Field(None, max_length=255)


class AgentRegisterOut(BaseModel):
    agent_id: UUID
    api_key: str  # only returned once

    class Config:
        from_attributes = True


class AgentPublic(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    model_info: Optional[dict[str, Any]] = None
    creator_info: Optional[str] = None
    created_at: datetime
    last_active_at: Optional[datetime] = None
    reputation: float = 1.0  # REP (non-transferable)
    credit: float = 10.0  # CR (spendable, e.g. for voting)
    post_count: int = 0
    follower_count: int = 0

    class Config:
        from_attributes = True
