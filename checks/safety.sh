#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3
args=("${1:-check}")
if [ "${LOOP_DRY_RUN:-1}" = 0 ] && [ "${1:-check}" = check ]; then args+=(--require-game); fi
exec "$PY" "$ROOT/checks/safety.py" "${args[@]}"
