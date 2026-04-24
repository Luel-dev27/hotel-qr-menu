#!/bin/sh
set -eu

cd /app/backend

if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  echo "DJANGO_SECRET_KEY must be set before starting the container."
  exit 1
fi

case "${DJANGO_SECRET_KEY}" in
  django-insecure-*|change-this-*)
    echo "DJANGO_SECRET_KEY is still using an unsafe placeholder."
    exit 1
    ;;
esac

python - <<'PY'
import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django import setup

setup()

from django.db import connections

deadline = time.time() + 60

while True:
    try:
        connections["default"].ensure_connection()
        break
    except Exception as exc:
        if time.time() >= deadline:
            raise SystemExit(f"Database connection failed: {exc}")
        print(f"Waiting for database: {exc}")
        time.sleep(2)
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers "${GUNICORN_WORKERS:-3}"
