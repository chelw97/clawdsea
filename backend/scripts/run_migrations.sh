#!/bin/sh
# Run Alembic migrations (sync URL for psycopg2)
export DATABASE_URL="${DATABASE_URL:-postgresql://clawdsea:clawdsea@localhost:5432/clawdsea}"
# Convert async URL to sync for Alembic
export DATABASE_URL="${DATABASE_URL/postgresql+asyncpg/postgresql}"
cd /app && alembic upgrade head
