#!/usr/bin/env bash
set -o errexit
set -o pipefail

echo "[start.sh] Render startup — $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date)"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "[start.sh] AVISO: DATABASE_URL não definida — SQLite (dados não persistem). Configure PostgreSQL no Dashboard."
else
  echo "[start.sh] DATABASE_URL definida (PostgreSQL)."
fi

echo "[start.sh] Executando migrate..."
python manage.py migrate --noinput
echo "[start.sh] Migrate concluído."

python manage.py ensure_superuser || true

echo "[start.sh] Iniciando gunicorn na porta ${PORT:-8000}..."
exec gunicorn wsgi:application --bind "0.0.0.0:${PORT:-8000}"
