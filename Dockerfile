FROM python:3.12.0-slim-bullseye as python-base

# Environ
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="${PATH}:/root/.local/bin" \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache

RUN curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
RUN apt-get update
RUN apt-get -y install make

# Create stage for Poetry installation
FROM python-base as poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
	&& $POETRY_VENV/bin/pip install poetry

# Create a new stage from the base python image
FROM python-base as futuramaapi-app

ARG APP_USER=userapp
ARG WORK_DIR=/app

# Copy Poetry to app image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR ${WORK_DIR}

# Copy Dependencies
COPY . ${WORK_DIR}

# Install Dependencies
RUN poetry install --no-interaction --no-cache --without dev --without test

EXPOSE 8000

# Add user
RUN groupadd \
    --system ${APP_USER} \
    && useradd --no-log-init --system --gid ${APP_USER} ${APP_USER}

# Set project user
USER ${APP_USER}:${APP_USER}

# Main launch command
CMD ["./docker-entrypoint.sh"]
