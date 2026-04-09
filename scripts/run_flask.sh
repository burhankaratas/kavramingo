#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -d "$ROOT_DIR/venv" ]]; then
  echo "Python venv bulunamadi: $ROOT_DIR/venv" >&2
  echo "Olusturmak icin: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

cd "$ROOT_DIR"
source "$ROOT_DIR/venv/bin/activate"
export LD_LIBRARY_PATH=/opt/lampp/lib:${LD_LIBRARY_PATH:-}
exec python3 app.py
