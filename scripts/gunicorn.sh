#!/usr/bin/env bash
set -euo pipefail

export FLASK_APP=run:app
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
