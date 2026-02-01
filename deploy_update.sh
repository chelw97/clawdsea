#!/bin/bash
set -e

git pull
sudo docker compose up -d --build backend
sh frontend/deploy.sh
