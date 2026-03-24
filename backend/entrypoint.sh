#!/bin/sh
set -e

echo "Waiting for database..."
MAX_RETRIES=15
RETRY=0

until python manage.py migrate 2>&1; do
  RETRY=$((RETRY + 1))
  if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
    echo "Database not ready after $MAX_RETRIES attempts. Exiting."
    exit 1
  fi
  echo "DB not ready — retrying in 2s ($RETRY/$MAX_RETRIES)"
  sleep 2
done

echo "Running seed_dev..."
python manage.py seed_dev

exec "$@"
