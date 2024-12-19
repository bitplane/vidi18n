#!/usr/bin/env bash

set -e

# activate venv
source .venv/bin/activate

# install our app
python3 -m pip install -e ./python/[dev,download,manager]

touch .venv/.installed
