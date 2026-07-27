#!/usr/bin/env bash

set -e

runtime_dir="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
podman_socket="$runtime_dir/podman/podman.sock"

if ! podman --remote --url "unix://$podman_socket" info >/dev/null 2>&1; then
    rm -f "$podman_socket"
    mkdir -p "$(dirname "$podman_socket")"
    podman system service --time=0 "unix://$podman_socket" >/dev/null 2>&1 &
    for _ in $(seq 1 50); do
        [ -S "$podman_socket" ] && break
        sleep 0.1
    done
fi

if [ ! -S "$podman_socket" ]; then
    echo "The rootless Podman API socket did not become ready." >&2
    exit 1
fi

export DOCKER_HOST="unix://$podman_socket"
exec podman compose --file compose.yaml "$@"
