#!/bin/sh
set -e
# Sync URL for Alembic (psycopg2) - POSIX sed, no bash substitution
SYNC_URL=$(echo "$DATABASE_URL" | sed 's/postgresql+asyncpg/postgresql/')
export DATABASE_URL_SYNC="$SYNC_URL"
# Run migrations (Alembic reads DATABASE_URL from env; we need to pass sync URL)
# env.py uses settings.database_url and replaces +asyncpg
cd /app && alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
