#!/usr/bin/env bash

# locale
make messages-compile

# Migrations
alembic upgrade head

hypercorn -b :$PORT main:app
