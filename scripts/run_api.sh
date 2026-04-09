#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/app/clients/ProjeTbtk"

if [[ ! -f "$API_DIR/artisan" ]]; then
  echo "Laravel API dizini bulunamadi: $API_DIR" >&2
  exit 1
fi

cd "$API_DIR"
exec /opt/lampp/bin/php artisan serve --host=127.0.0.1 --port=8000
