#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILE="docker-compose.prod.yml"

show_logs() {
  local service="$1"
  echo
  echo "Recent ${service} logs:"
  docker compose -f "${COMPOSE_FILE}" logs --tail=80 "${service}" || true
}

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "Run this script from the repository root, for example /opt/finmateuz." >&2
  exit 1
fi

if [[ ! -f ".env" ]]; then
  echo ".env is missing. Create it from .env.example or your server template, then fill production secrets first." >&2
  exit 1
fi

echo "Pulling latest code..."
git pull --ff-only

echo "Building and starting production stack..."
docker compose -f "${COMPOSE_FILE}" up --build -d

echo "Container status:"
docker compose -f "${COMPOSE_FILE}" ps

echo "Checking API health..."
if ! curl -fsS http://127.0.0.1:8000/health >/dev/null; then
  show_logs api
  exit 1
fi

echo "Checking web health..."
if ! curl -fsSI http://127.0.0.1:3000 >/dev/null; then
  show_logs web
  exit 1
fi

echo "Production stack is running."
