#!/usr/bin/env bash

# Migrations
python -m alembic upgrade head

python -m futuramaapi -b :"${PORT:-8080}" "$@"
