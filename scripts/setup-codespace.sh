#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Explicit development container only. No provider accounts or deployment keys.
if [[ "${MOUCHAK_ENV:-development}" == production ]]; then
  echo "This setup is development only." >&2
  exit 1
fi
if ! command -v pnpm >/dev/null || [[ "$(pnpm --version)" != 11.25.0 ]]; then
  sudo npm install --global pnpm@11.25.0
fi
pnpm install --frozen-lockfile
if [[ ! -x .venv/bin/python ]]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r requirements-python.txt
.venv/bin/python scripts/download-models.py
echo "Ready. Run: pnpm dev --host 0.0.0.0"
echo "Open port 3000 in the Ports tab; keep its visibility Private. Do not forward 8000."
