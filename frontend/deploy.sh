#!/bin/sh
# 前端部署脚本：构建并重启 PM2（在 EC2 上执行）
set -e
cd "$(dirname "$0")"
npm install
npm run build
pm2 restart clawdsea-frontend
echo "Frontend deployed."
