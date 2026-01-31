"""Vote request/response schemas."""
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.vote import VoteTargetType


class VoteCreateIn(BaseModel):
    target_type: VoteTargetType
    target_id: UUID
    value: int = Field(..., ge=-1, le=1)  # +1 or -1
