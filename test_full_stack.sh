#!/usr/bin/env bash
# Start full stack: backend (Docker: db + redis + API) + frontend (Next.js dev).
# Usage: ./test_full_stack.sh
# Stop: Ctrl+C (stops frontend); then: docker compose down

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "=== 1. Backend (Docker: Postgres + Redis + FastAPI) ==="
docker compose up -d
echo "Waiting for backend health..."
for i in {1..30}; do
  if curl -sS -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null | grep -q 200; then
    echo "Backend OK at $BACKEND_URL"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "Backend did not become healthy. Check: docker compose logs backend"
    exit 1
  fi
  sleep 1
done

echo ""
echo "=== 2. Frontend (.env.local) ==="
ENV_LOCAL="$SCRIPT_DIR/frontend/.env.local"
if [[ ! -f "$ENV_LOCAL" ]]; then
  echo "Creating $ENV_LOCAL (API_URL=$BACKEND_URL)"
  cat > "$ENV_LOCAL" << EOF
API_URL=$BACKEND_URL
NEXT_PUBLIC_API_URL=$BACKEND_URL
EOF
else
  echo "Using existing $ENV_LOCAL"
fi

echo ""
echo "=== 3. Frontend (Next.js dev server) ==="
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: http://localhost:3000 (or next free port)"
echo "  Stop backend later: docker compose down"
echo ""
cd "$SCRIPT_DIR/frontend"
npm ci 2>/dev/null || npm install
exec npm run dev
