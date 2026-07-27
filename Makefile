# the things that don't have output files or run every time
.PHONY: help all install test test-integration dev coverage clean node node-local podman models \
		pre-commit update-pre-commit


all: dev coverage ## builds everything

dev: install ## install it

install: .venv/.installed ## installs the venv and the project packages

test: .venv/.installed  ## run the project's tests
	build/test.sh

test-integration: .venv/.installed ## run the progressive Podman integration test
	build/test-integration.sh

coverage: .venv/.installed build/coverage.sh  ## build the html coverage report
	build/coverage.sh

clean:  ## delete caches and the venv
	build/clean.sh

pre-commit: .git/hooks/pre-commit ## install pre-commit into the git repo

update-pre-commit: build/update-pre-commit.sh ## autoupdate pre-commit
	build/update-pre-commit.sh

node: build/podman.sh compose.yaml ## build and run the rootless node
	build/podman.sh

node-local: build/podman-local.sh compose.yaml compose.local.yaml ## run with local models
	build/podman-local.sh

podman: node ## alias for the node target

models: compose.yaml ## download local processing models into the Podman volume
	build/podman-compose.sh --profile models run --rm models

docs: .docs/index.html ## build the documentation


# Caching doesn't work if we depend on PHONY targets

.venv/.installed: */pyproject.toml .venv/bin/activate build/install.sh
	build/install.sh

.venv/bin/activate:
	build/venv.sh

.git/hooks/pre-commit: build/install-pre-commit.sh
	build/install-pre-commit.sh

.docs/index.html: .venv/.installed build/docs.sh mkdocs.yml $(shell find -name '*.md')
	build/docs.sh

help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
