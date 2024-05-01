#!/usr/bin/env bash

if [ -z "${PORT}" ]
then
  PORT=8080
fi

# Migrations
make migrate

poetry run hypercorn -b :$PORT -k uvloop futuramaapi.main:app
