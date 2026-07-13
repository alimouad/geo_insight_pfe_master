#!/usr/bin/env bash
# Sync the local repo to the DigitalOcean droplet and rebuild/restart the
# production stack. Run from the repo root: ./deploy.sh
set -euo pipefail

DROPLET_IP="134.122.61.233"
SSH_KEY="$HOME/.ssh/id_ed25519"
REMOTE_DIR="/root/geoinsight"

echo "==> Syncing code to droplet..."
rsync -az --delete \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'dist' \
  --exclude 'exports_storage' \
  --exclude 'backend/.env' \
  --exclude 'backend/.env.prod' \
  --exclude 'frontend/app/.env' \
  --exclude 'conception' \
  -e "ssh -i $SSH_KEY" \
  ./ "root@${DROPLET_IP}:${REMOTE_DIR}/"

echo "==> Rebuilding and restarting containers..."
ssh -i "$SSH_KEY" "root@${DROPLET_IP}" "cd ${REMOTE_DIR} && docker compose -f docker-compose.prod.yml up -d --build"

echo "==> Done. Site: http://${DROPLET_IP}"
