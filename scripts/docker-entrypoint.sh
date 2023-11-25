#!/usr/bin/env bash
source .venv/bin/activate
echo "Apply database migrations..."
python3 manage.py migrate --skip-checks --no-input

echo "Run server"
.venv/bin/gunicorn nomsable.wsgi \
          --name nomsable \
          -b 127.0.0.1:8000
