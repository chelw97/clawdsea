#!/bin/sh
# 后端重启脚本：拉代码、重新构建并启动 backend（在 EC2 上执行）
set -e
cd "$(dirname "$0")"

echo "Pulling latest code..."
git pull

echo "Rebuilding and starting backend..."
sudo docker compose up -d --build backend

echo "Waiting for backend to be ready..."
sleep 3
sudo docker compose ps

if curl -sf http://localhost:8000/health > /dev/null; then
  echo "Backend is up. /api/stats: $(curl -s http://localhost:8000/api/stats)"
else
  echo "Backend may still be starting. Check: docker compose logs -f backend"
fi
