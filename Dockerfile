FROM python:3.12.0-slim-bullseye

# Environ
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Arguments
ARG APP_USER=qworpa
ARG WORK_DIR=/app

# Install OS dependencies
COPY install-dependencies.sh /tmp
RUN . /tmp/install-dependencies.sh

# Install python environ
RUN python3 -m venv $VIRTUAL_ENV
COPY requirements.txt /tmp
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt

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

# Set project user
USER ${APP_USER}:${APP_USER}

# Compile messages
RUN cd ${WORK_DIR}; make messages-compile

# Main launch command
CMD ["./docker-entrypoint.sh"]
