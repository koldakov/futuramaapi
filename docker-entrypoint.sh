#!/usr/bin/env bash

if [ -z "${PORT}" ]
then
  PORT=8080
fi

# locale
make messages-compile

# Migrations
alembic upgrade head

hypercorn -b :$PORT app.main:app
