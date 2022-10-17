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
