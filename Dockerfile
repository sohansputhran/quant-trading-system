# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

# System deps (add build tools only if you need them later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git tini \
 && rm -rf /var/lib/apt/lists/*

# Prevent Python from writing .pyc & use unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Workdir
WORKDIR /app

# Copy only requirements first for better Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python deps (add --extra-index-url or private indexes if needed)
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project
COPY . /app

# Default shell (can be overridden by docker-compose command)
SHELL ["/bin/bash", "-lc"]

# Create a non-root user (good practice)
RUN useradd -m runner && chown -R runner:runner /app
USER runner

# Entrypoint via tini for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]
# Default: open a shell; override with `command:` in docker-compose
CMD ["bash"]
