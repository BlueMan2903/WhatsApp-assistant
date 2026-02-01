# --- STAGE 1: Builder ---
# This stage installs dependencies into a virtual environment.
FROM python:3.11-slim AS builder

# Install uv, our package manager
RUN pip install uv

# Set up a non-root user for security
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Create a virtual environment
RUN uv venv .venv

# Copy only the dependency definition files to leverage Docker's cache
COPY pyproject.toml uv.lock ./

# Install dependencies into the virtual environment using the lock file
# This is the core of the reproducible build
RUN . .venv/bin/activate && uv sync

# --- STAGE 2: Final Image ---
# This stage copies the pre-installed dependencies and the app code.
FROM python:3.11-slim

# Set up the same non-root user
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser

# Copy the virtual environment with all its dependencies from the builder stage
COPY --from=builder /home/appuser/.venv ./.venv

# Copy the rest of the application code
COPY . .

# Set the PATH to include the virtual environment's binaries
# This ensures that 'gunicorn' and other packages are found
ENV PATH="/home/appuser/.venv/bin:$PATH"

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]