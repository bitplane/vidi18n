#!/usr/bin/env bash


REDIS_HOST="redis"
GID=$(id -g)

export REDIS_HOST=$REDIS_HOST
export GID=$GID
export UID=$UID || true

set -e

docker compose up --build
