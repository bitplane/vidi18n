#!/usr/bin/env bash

set -e

device="${1:-cpu}"
project_name="vidi18n-model-test-$$"
files=(--file compose.model-test.yaml)

if [ "$device" = "gpu" ]; then
    podman run --rm \
        --device nvidia.com/gpu=all \
        --security-opt label=disable \
        docker.io/nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04 \
        nvidia-smi -L
    files+=(--file compose.gpu.yaml)
elif [ "$device" != "cpu" ]; then
    echo "Usage: $0 [cpu|gpu]" >&2
    exit 2
fi

cleanup() {
    set +e
    build/podman-compose.sh \
        --project-name "$project_name" \
        "${files[@]}" \
        --profile test \
        down --volumes
    if podman container exists "${project_name}-redis-1"; then
        podman rm --force "${project_name}-redis-1"
        build/podman-compose.sh \
            --project-name "$project_name" \
            "${files[@]}" \
            --profile test \
            down --volumes
    fi
    set -e
}
trap cleanup EXIT

build/podman-compose.sh \
    --project-name "$project_name" \
    "${files[@]}" \
    --profile test \
    up --build --detach

VIDI18N_EXPECTED_DEVICE="$device" \
    .venv/bin/python python/tests/integration/model_benchmark.py
