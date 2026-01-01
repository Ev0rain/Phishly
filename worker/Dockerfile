FROM docker.io/library/python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV for Python dependency management
RUN pip install --no-cache-dir uv

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using UV
RUN uv pip install --system -r requirements.txt

# Copy worker code
COPY tasks.py .
COPY database.py .
COPY email_renderer.py .
COPY email_sender.py .

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose.yml)
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
