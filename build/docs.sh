#!/usr/bin/bash

source .venv/bin/activate

set -e

pushd python/src
pydoc-markdown -p python > ../../docs/pydoc.md
popd

mkdocs build
#mkdocs gh-deploy
