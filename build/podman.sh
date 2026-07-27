#!/usr/bin/env bash

set -e

exec podman compose --file compose.yaml up --build "$@"
