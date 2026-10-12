SHELL = /bin/bash

help: # Display this message
	@sed -ne '/@sed/!s/# //p' $(MAKEFILE_LIST)

install-dev: # Install DEV/TEST Environ and dependencies
	@echo "Installing dependencies"
	@uv sync

test: # Run tests
	@uv run pytest

migrate: # Migrate
	@uv run alembic upgrade head
