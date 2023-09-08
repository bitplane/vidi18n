#!/usr/bin/env bash

set -e

source .venv/bin/activate

pre-commit autoupdate
