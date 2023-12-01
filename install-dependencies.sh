#!/bin/bash

apt-get update
apt-get install --assume-yes --no-install-recommends \
    make

apt-get clean
rm -rf /var/lib/apt/lists/*
