#!/usr/bin/env bash
set -o errexit

# Start Gunicorn with 4 workers, 120s timeout, bind to 0.0.0.0:$PORT
exec gunicorn -w 4 -b 0.0.0.0:"${PORT:-5000}" --timeout 120 wsgi:app
