FROM python:3.12.0-slim-bullseye AS futuramaapi-app

ARG APP_USER=futuramaapi
ARG WORK_DIR=/app

# Environ
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_NO_CACHE=1 \
    PATH="${WORK_DIR}/.venv/bin:${PATH}"

# Copy uv to app image
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

WORKDIR ${WORK_DIR}

# Install Dependencies (cached until the lock file changes)
COPY pyproject.toml uv.lock ${WORK_DIR}/
RUN uv sync --locked --no-default-groups --no-install-project

# Copy project and install it
COPY . ${WORK_DIR}
RUN uv sync --locked --no-default-groups

EXPOSE 8000

# Add user
RUN groupadd \
    --system ${APP_USER} \
    && useradd --no-log-init --system --gid ${APP_USER} ${APP_USER}

# Set project user
USER ${APP_USER}:${APP_USER}

# Main launch command
CMD ["./docker-entrypoint.sh"]
