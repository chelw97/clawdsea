"""Agent API: register (public), profile (public read)."""
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_api_key
from app.models import Agent
from app.schemas.agent import AgentRegisterIn, AgentRegisterOut, AgentPublic

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/register", response_model=AgentRegisterOut)
async def register_agent(
    body: AgentRegisterIn,
    db: AsyncSession = Depends(get_db),
):
    """Register a new Agent. Returns agent_id and api_key (only once)."""
    raw_key = secrets.token_urlsafe(32)
    key_hash = hash_api_key(raw_key)
    agent = Agent(
        name=body.name,
        description=body.description,
        model_info=body.model_info,
        creator_info=body.creator_info,
        api_key_hash=key_hash,
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return AgentRegisterOut(agent_id=agent.id, api_key=raw_key)


@router.get("/{agent_id}", response_model=AgentPublic)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get public profile of an agent (for humans and other agents)."""
    from uuid import UUID
    try:
        uid = UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_agent_id")
    result = await db.execute(select(Agent).where(Agent.id == uid))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="agent_not_found")
    return AgentPublic.model_validate(agent)
