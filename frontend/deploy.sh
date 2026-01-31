#!/bin/sh
# Frontend deploy script: build and restart PM2 (run on EC2)
set -e
cd "$(dirname "$0")"
npm install
npm run build
pm2 restart clawdsea-frontend
echo "Frontend deployed."
