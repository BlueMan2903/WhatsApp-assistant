# Docker/Dockerfile
FROM python:3.11-slim AS builder

# Install Build Essentials
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create a non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Force uv to use the correct environment path
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"

# Create the venv explicitly
RUN uv venv /opt/venv --python 3.11

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies - this now includes python-bidi from your lockfile
RUN uv sync --frozen --no-install-project

FROM python:3.11-slim

# PATCH HIGH VULNERABILITIES & FIX LOCALE
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Create the user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Copy the safe venv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose the Flask port
EXPOSE 5000

# Run Gunicorn with threading and extended timeout
# -w 1: Single master worker
# --threads 4: Handles concurrent I/O (like large image uploads)
# --timeout 120: Prevents worker suicide during slow transfers
CMD ["gunicorn", "-w", "1", "--threads", "4", "--timeout", "120", "-b", "0.0.0.0:5000", "app:app"]