# Clawdsea Backend - MVP
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

# Use sync URL for migrations (psycopg2)
ENV DATABASE_URL=postgresql://clawdsea:clawdsea@db:5432/clawdsea
ENV REDIS_URL=redis://redis:6379/0

EXPOSE 8000
COPY scripts/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
