#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/app/clients/ProjeTbtk"

echo "[1/6] XAMPP MySQL durumu kontrol ediliyor..."
/opt/lampp/xampp status | sed -n '1,20p' >/dev/null 2>&1 || true

echo "[2/6] Veritabanlari hazirlaniyor..."
/opt/lampp/bin/mysql -u root -e "CREATE DATABASE IF NOT EXISTS kavramingo CHARACTER SET utf8mb4 COLLATE utf8mb4_turkish_ci;"
/opt/lampp/bin/mysql -u root -e "CREATE DATABASE IF NOT EXISTS kavramingo_content CHARACTER SET utf8mb4 COLLATE utf8mb4_turkish_ci;"

echo "[3/6] Flask .env kontrol ediliyor..."
if [[ ! -f "$ROOT_DIR/.env" ]]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "  - .env olusturuldu, KAVRAM_API_TOKEN alanini doldurman gerekiyor."
fi

echo "[4/6] Laravel .env kontrol ediliyor..."
if [[ ! -f "$API_DIR/.env" ]]; then
  cp "$API_DIR/.env.example" "$API_DIR/.env"
fi

echo "[5/6] Laravel migration..."
cd "$API_DIR"
/opt/lampp/bin/php artisan migrate --force

echo "[6/6] Hazir."
echo "API:   $ROOT_DIR/scripts/run_api.sh"
echo "Flask: $ROOT_DIR/scripts/run_flask.sh"
