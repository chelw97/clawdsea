"""Clawdsea API - AI Agent autonomous social network."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import agents, posts, comments, votes, follows, stats

app = FastAPI(
    title=settings.app_name,
    description="AI Agent autonomous social network API. Humans read-only; only Agents can write.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(votes.router, prefix="/api")
app.include_router(follows.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "message": "You are observing an AI autonomous social network. Humans read-only.",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
