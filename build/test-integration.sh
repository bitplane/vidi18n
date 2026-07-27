#!/usr/bin/env bash

set -e

project_name="vidi18n-test-$$"

cleanup() {
    set +e
    build/podman-compose.sh \
        --project-name "$project_name" \
        --file compose.test.yaml \
        --profile test \
        down --volumes
    if podman container exists "${project_name}-redis-1"; then
        # Some rootless Podman releases fail to tear down Redis' netns through
        # the delegated Compose provider. Direct removal is reliable.
        podman rm --force "${project_name}-redis-1"
        build/podman-compose.sh \
            --project-name "$project_name" \
            --file compose.test.yaml \
            --profile test \
            down --volumes
    fi
    set -e
}
trap cleanup EXIT

build/podman-compose.sh \
    --project-name "$project_name" \
    --file compose.test.yaml \
    --profile test \
    up --build --detach

.venv/bin/python python/tests/integration/progressive.py
