#!/bin/bash
set -ex

echo "Running Alembic migrations..."
alembic upgrade head
echo "Alembic done. Starting app..."

python -m src.bot.main
