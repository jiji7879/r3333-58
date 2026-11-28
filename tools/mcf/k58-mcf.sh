#!/usr/bin/env bash
# Separate opt-in MCF entry point. Stock k58.sh/run/finalise are not modified.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
if [[ -x "$ROOT/.venv/bin/python" ]]; then PY=$ROOT/.venv/bin/python; else PY=${PYTHON:-python3}; fi
export PYTHONPATH="$ROOT/mcf:$ROOT/color-resolved-wallcc:$ROOT/color-resolved-wallcc/frozen${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
exec "$PY" "$ROOT/mcf/driver.py" "$@"
