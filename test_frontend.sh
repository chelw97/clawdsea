#!/usr/bin/env bash
# 本机测试前端：安装依赖、构建，可选连远程后端(https://clawdsea.com) 启动 dev
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
ENV_LOCAL="$FRONTEND_DIR/.env.local"
BACKEND_URL="${BACKEND_URL:-https://clawdsea.com}"

cd "$FRONTEND_DIR"

# 若无 .env.local，生成一个指向远程后端，便于本机测试
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
