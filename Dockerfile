FROM python:3.12.0-slim-bullseye

# Environ
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Arguments
ARG APP_USER=qworpa
ARG WORK_DIR=/app

# Install dependencies
RUN apt-get update
RUN apt-get -y install make

# Add user
RUN groupadd \
    --system ${APP_USER} \
    && useradd --no-log-init --system --gid ${APP_USER} ${APP_USER}

# Copy project files to the work dir
COPY ./ ${WORK_DIR}

# Set owner to the project
RUN chown -R ${APP_USER}:${APP_USER} ${WORK_DIR}

# Set work dir
WORKDIR ${WORK_DIR}

EXPOSE 8000

# Install project
RUN make install

# Set project user
USER ${APP_USER}:${APP_USER}

# Main launch command
CMD ["./docker-entrypoint.sh"]
