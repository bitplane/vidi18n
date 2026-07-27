#!/usr/bin/env bash

set -e

exec build/podman-compose.sh up --build "$@"
