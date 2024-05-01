SHELL = /bin/bash
PYTHON = python3.12

help: # Display this message
	@sed -ne '/@sed/!s/# //p' $(MAKEFILE_LIST)

install-dev: # Install DEV/TEST Environ and dependencies
	@echo "Upgrading pip"
	@$(PYTHON) -m pip install --upgrade pip
	@echo "Installing poetry"
	@$(PYTHON) -m pip install poetry
	@echo "Installing dependencies"
	@$(PYTHON) -m poetry install

install: # Install Environ and dependencies
	@echo "Upgrading pip"
	@$(PYTHON) -m pip install --upgrade pip
	@echo "Installing poetry"
	@$(PYTHON) -m pip install poetry
	@echo "Installing dependencies"
	@$(PYTHON) -m poetry install --without dev --without test

test: # Run tests
	@poetry run $(PYTHON) -m pytest

migrate: # Migrate
	@poetry run $(PYTHON) -m alembic upgrade head
