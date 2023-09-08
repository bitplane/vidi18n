#!/usr/bin/env bash

set -e

source .venv/bin/activate

coverage run -m pytest ./*/tests
coverage html
