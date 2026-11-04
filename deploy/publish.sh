#!/usr/bin/env bash
# Publish Marksweep to the shared Hetzner box -> https://meta.vantapointlabs.com
#   SERVER=root@37.27.202.168 bash deploy/publish.sh
# Conventions (infra/README.md): app in /opt/marksweep, container on the existing Caddy network, Caddy drop-in in
# /opt/caddy-sites, zero-downtime `caddy reload`. Touches nothing else on the box. Needs ./.env with MODEL_API_KEY
# (or MARKSWEEP_FIXTURE=1) and MARKSWEEP_TOKEN.
set -euo pipefail
HOST=${SERVER:-root@37.27.202.168}
APP_DIR=/opt/marksweep
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/.env" ] || { echo "missing $ROOT/.env"; exit 1; }

echo "==> rsync sources to $HOST:$APP_DIR"
ssh "$HOST" "mkdir -p $APP_DIR /opt/caddy-sites"
rsync -az --delete --copy-links --exclude .venv --exclude data --exclude __pycache__ --exclude .pytest_cache \
  --exclude '*.egg-info' --exclude .git --exclude .env --exclude submission "$ROOT/" "$HOST:$APP_DIR/"
rsync -az "$ROOT/.env" "$HOST:$APP_DIR/deploy/.env"

echo "==> build + start"
ssh "$HOST" "cd $APP_DIR/deploy && docker compose build marksweep && docker compose up -d marksweep"

echo "==> caddy drop-in + reload"
rsync -az "$ROOT/deploy/marksweep.caddy" "$HOST:/opt/caddy-sites/marksweep.caddy"
ssh "$HOST" "cd /opt/compass/deploy && docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile"

echo "==> health"
sleep 4
ssh "$HOST" "docker exec marksweep python -c 'import urllib.request;print(urllib.request.urlopen(\"http://127.0.0.1:8000/healthz\").read().decode())'"
curl -sS -o /dev/null -w "https://meta.vantapointlabs.com  HTTP %{http_code}\n" --max-time 30 https://meta.vantapointlabs.com/ || echo "  (first HTTPS hit may lag while the certificate is issued)"
