#!/usr/bin/env bash
# Simple setup script for tg-bot-service

set -e

# Copy .env.example if .env does not exist
if [ ! -f .env ]; then
  echo "Copying .env.example to .env"
  cp .env.example .env
fi

# Ensure required directories exist
mkdir -p sessions userbot_media

# Initialize Telegram session (requires python3)
if command -v python3 >/dev/null 2>&1; then
  python3 init_session.py
else
  echo "python3 not found. Please install Python 3 to generate the session."
fi

# Determine docker compose command
if command -v docker-compose >/dev/null 2>&1; then
  compose_cmd="docker-compose"
else
  compose_cmd="docker compose"
fi

# Build images and start services
$compose_cmd build
$compose_cmd up -d

echo "tg-bot-service is up and running."
