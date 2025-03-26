#!/usr/bin/env bash

# Migrations
make migrate

poetry run python -m futuramaapi -b :"${PORT:-8080}" "$@"
