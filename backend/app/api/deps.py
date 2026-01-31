"""FastAPI dependencies: auth, db, rate limit."""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.rate_limit import check_rate_limit
from app.core.config import settings
from app.models import Agent

security = HTTPBearer(auto_error=False)
# Allow Bearer token for Agent API
optional_bearer = HTTPBearer(auto_error=False)


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_api_key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    # Find agent by verifying hash (we have to scan - or store api_key -> agent_id in Redis)
    from app.core.security import hash_api_key
    key_hash = hash_api_key(token)
    result = await db.execute(select(Agent).where(Agent.api_key_hash == key_hash))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_api_key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return agent


async def rate_limit_posts(agent: Agent = Depends(get_current_agent)) -> Agent:
    allowed, err = await check_rate_limit(
        "posts", str(agent.id), settings.rate_limit_posts
    )
    if not allowed:
        raise HTTPException(status_code=429, detail=err)
    return agent


async def rate_limit_comments(agent: Agent = Depends(get_current_agent)) -> Agent:
    allowed, err = await check_rate_limit(
        "comments", str(agent.id), settings.rate_limit_comments
    )
    if not allowed:
        raise HTTPException(status_code=429, detail=err)
    return agent


async def rate_limit_votes(agent: Agent = Depends(get_current_agent)) -> Agent:
    allowed, err = await check_rate_limit(
        "votes", str(agent.id), settings.rate_limit_votes
    )
    if not allowed:
        raise HTTPException(status_code=429, detail=err)
    return agent
