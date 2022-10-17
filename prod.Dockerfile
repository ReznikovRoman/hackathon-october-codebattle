# Base image
FROM python:3.10-slim as builder

# Configure environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        gcc \
        make \
        libpq-dev \
        musl-dev \
        libc-dev \
        libcurl4-gnutls-dev \
        librtmp-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY ./requirements/requirements.txt /app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# Final

# Base image
FROM python:3.10-slim

# Configure environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive
# CodeBattle Hackathon
# App
ENV HOC_BUILD_NUMBER=0.1.4
ENV HOC_DEBUG=0
ENV HOC_ENVIRONMENT=prod
ENV HOC_LOG_LEVEL=INFO
ENV HOC_PROJECT_NAME=hackathon-codebattle
ENV HOC_PROJECT_BASE_URL=http://51.250.36.15
# API
ENV HOC_API_V1_STR=/api/v1
ENV HOC_API_HEALTHCHECK_PATH=/healthcheck
ENV HOC_API_DEFAULT_PAGINATION_LIMIT=10
ENV HOC_API_CONFIG_DEPENDENCY_KEY=config
ENV HOC_API_REDIS_CLIENT_DEPENDENCY_KEY=redis_client
ENV HOC_API_DB_SESSION_DEPENDENCY_KEY=db_session
# Database
ENV HOC_DB_ECHO=false
ENV HOC_DB_ECHO_POOL=false
ENV HOC_DB_POOL_DISABLE=false
ENV HOC_DB_POOL_MAX_OVERFLOW=10
ENV HOC_DB_POOL_SIZE=5
ENV HOC_DB_POOL_TIMEOUT=30
ENV HOC_DB_HOST=db
ENV HOC_DB_PORT=5432
ENV HOC_DB_NAME=hackathon-october-codebattle
ENV HOC_DB_USER=hackathon
ENV HOC_DB_PASSWORD=codebattle
# Redis
ENV HOC_REDIS_HOST=redis
ENV HOC_REDIS_PORT=6379
ENV HOC_REDIS_DB=0
ENV HOC_REDIS_DEFAULT_CHARSET=utf-8
ENV HOC_REDIS_DECODE_RESPONSES=1
ENV HOC_REDIS_RETRY_ON_TIMEOUT=1
# OpenAPI
ENV HOC_OPENAPI_TITLE="Hackathon CodeBattle API"
ENV HOC_OPENAPI_VERSION=0.1.4
ENV HOC_OPENAPI_CONTACT_NAME="Roman Reznikov"
ENV HOC_OPENAPI_CONTACT_EMAIL=romanreznikov.am@gmail.com
# Server
ENV HOC_SERVER_PORT=80
ENV HOC_SERVER_NAME=localhost
ENV HOC_SERVER_HOSTS=http://51.250.36.15
ENV HOC_USE_STUBS=0
ENV HOC_TESTING=0
ENV HOC_CI=0

# Create all appropriate directories
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        gcc \
        make \
        libpq-dev \
        musl-dev \
        libc-dev \
        libcurl4-gnutls-dev \
        librtmp-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies from the previous stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# Expose port
EXPOSE 80

# Copy configuration files
COPY ./scripts /app/scripts
RUN chmod +x /app/scripts/docker/entrypoint.prod.sh

# Copy project
COPY . .

# Spin up server
WORKDIR /app/src
CMD ["/app/scripts/docker/entrypoint.prod.sh"]
