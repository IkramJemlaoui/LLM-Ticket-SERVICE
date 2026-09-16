#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

cd "$PROJECT_ROOT"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Creating the project virtual environment..."
  python3 -m venv "$PROJECT_ROOT/.venv"
fi

if ! "$VENV_PYTHON" -c "import streamlit, sklearn" >/dev/null 2>&1; then
  echo "Installing project dependencies into .venv..."
  "$VENV_PYTHON" -m pip install -r "$PROJECT_ROOT/requirements.txt"
fi

"$VENV_PYTHON" "$PROJECT_ROOT/scripts/seed_demo_data.py"

APP_PORT="${AEGISDESK_PORT:-$("$VENV_PYTHON" -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')}"
echo "Starting AegisDesk at http://localhost:$APP_PORT"
"$VENV_PYTHON" -m streamlit run "$PROJECT_ROOT/app/streamlit_app.py" --server.port "$APP_PORT"
