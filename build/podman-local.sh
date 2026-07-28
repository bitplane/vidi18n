#!/usr/bin/env bash

set -e

build/podman-compose.sh \
    --file compose.local.yaml \
    --profile models \
    run --build --rm models

exec build/podman-compose.sh \
    --file compose.local.yaml \
    up --build "$@"
