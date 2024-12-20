# the things that don't have output files or run every time
.PHONY: help all install test dev coverage clean \
		pre-commit update-pre-commit


all: dev coverage ## builds everything

dev: install ## install it

install: .venv/.installed ## installs the venv and the project packages

test: .venv/.installed  ## run the project's tests
	build/test.sh

coverage: .venv/.installed build/coverage.sh  ## build the html coverage report
	build/coverage.sh

clean:  ## delete caches and the venv
	build/clean.sh

pre-commit: .git/hooks/pre-commit ## install pre-commit into the git repo

update-pre-commit: build/update-pre-commit.sh ## autoupdate pre-commit
	build/update-pre-commit.sh

docker: build/docker.sh docker-compose.yml ## build and run docker compose environment
	build/docker.sh

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
