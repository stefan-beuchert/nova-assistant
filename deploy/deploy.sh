#!/usr/bin/env bash
# Auto-deploy poller: pulls and redeploys only when origin/master has moved.
# Run periodically by nova-deploy.timer -- see deploy/README.md for setup.
set -euo pipefail
cd "$(dirname "$0")/.."

exec 200>/tmp/nova_deploy.lock
flock -n 200 || { echo "$(date -Iseconds) deploy already running, skipping"; exit 0; }

git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "$(date -Iseconds) up to date, nothing to do"
  exit 0
fi

echo "$(date -Iseconds) new commits found ($LOCAL -> $REMOTE), pulling and redeploying"
git pull origin master

# Optional test gate: if this project has a suite, run it before rebuilding so a bad
# push never reaches the running containers. The PoC has no tests/ yet, so this is
# skipped; it activates automatically once a tests/ dir (and pytest) exist, matching
# Constellation's deploy gate.
if [ -d tests ]; then
  PYTEST=""
  if [ -x ".venv/bin/pytest" ]; then
    PYTEST=".venv/bin/pytest"
  elif command -v pytest >/dev/null 2>&1; then
    PYTEST="pytest"
  fi
  if [ -n "$PYTEST" ] && ! "$PYTEST" -q; then
    echo "$(date -Iseconds) tests failed after pull, aborting deploy (running version left untouched)"
    exit 1
  fi
fi

# Stamp the running version for GET /version (freshly-pulled commit + deploy time);
# compose passes these through to the container as APP_VERSION/APP_BUILD_TIME.
export GIT_SHA=$(git rev-parse --short HEAD)
export BUILD_TIME=$(date -u +%Y-%m-%dT%H:%MZ)

docker compose up -d --build
echo "$(date -Iseconds) deploy complete"
