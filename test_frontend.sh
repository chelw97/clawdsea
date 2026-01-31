#!/usr/bin/env bash
# Local frontend test: install deps, build, optionally start dev with remote backend (default http://localhost:8000)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
ENV_LOCAL="$FRONTEND_DIR/.env.local"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

cd "$FRONTEND_DIR"

# If no .env.local, create one pointing to remote backend for local testing
if [[ ! -f "$ENV_LOCAL" ]]; then
  echo "Creating $ENV_LOCAL (BACKEND_URL=$BACKEND_URL)"
  cat > "$ENV_LOCAL" << EOF
API_URL=$BACKEND_URL
NEXT_PUBLIC_API_URL=$BACKEND_URL
EOF
fi

echo "Installing dependencies..."
npm ci 2>/dev/null || npm install

echo "Building frontend..."
npm run build

echo "Frontend build OK."
echo ""

if [[ "${1:-}" == "--dev" ]]; then
  echo "Starting dev server at http://localhost:3000"
  exec npm run dev
fi

echo "To run dev server:  ./test_frontend.sh --dev   (or: cd frontend && npm run dev)"
echo "Then open:          http://localhost:3000"
echo "Override backend:   BACKEND_URL=https://other.com ./test_frontend.sh"
