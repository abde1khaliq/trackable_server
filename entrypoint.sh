#!/bin/bash
set -e

# `alembic upgrade head` is a no-op if the schema is already current, so it's
# safe to run in every service. This avoids a race where the worker or beat
# container starts querying the DB before the api container has migrated it.
echo "Running database migrations..."
alembic upgrade head

case "$1" in
  api)
    echo "Starting FastAPI server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
    ;;
  worker)
    echo "Starting Celery worker..."
    exec celery -A app.celery.celery_app worker --loglevel=info
    ;;
  beat)
    echo "Starting Celery beat scheduler..."
    exec celery -A app.celery.celery_app beat --loglevel=info
    ;;
  *)
    # Fallback: run whatever command was passed in directly
    exec "$@"
    ;;
esac