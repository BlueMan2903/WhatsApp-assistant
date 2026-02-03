# Docker/Dockerfile
FROM python:3.11-slim as builder

# --- FIX: Install Build Essentials AND libffi-dev ---
# build-essential: for GCC
# libffi-dev: for compiling cffi (required by google-auth/cryptography)
# curl: for downloading tools if needed
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

# Force uv to use the System Python (3.11)
ENV UV_PYTHON=python3.11
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"

# Create the venv explicitly
RUN uv venv /opt/venv --python 3.11

COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

FROM python:3.11-slim

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

# Run Gunicorn
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]