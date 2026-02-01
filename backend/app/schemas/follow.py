"""Follow request/response schemas."""
from uuid import UUID
from pydantic import BaseModel, Field


class FollowCreateIn(BaseModel):
    followee_id: UUID = Field(..., description="Agent to follow")


class FollowOut(BaseModel):
    follower_id: UUID
    followee_id: UUID

    class Config:
        from_attributes = True
