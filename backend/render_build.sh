#!/usr/bin/env bash
# render_build.sh
# Executed by Render on every deploy of the churchos-api service.

set -o errexit
set -o pipefail

echo "=== ChurchOS Backend Build ==="
echo "Python: $(python --version)"

export DJANGO_ENV=render

echo ""
echo "→ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "→ Collecting static files..."
python manage.py collectstatic --no-input

echo ""
echo "→ Running database migrations..."
python manage.py migrate --no-input

echo ""
echo "→ Seeding initial data..."
python manage.py setup_initial_data

echo ""
echo "=== Build complete ==="
