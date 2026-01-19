# Phishly Phishing Server Dockerfile
FROM docker.io/library/python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy requirements and install dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY server.py .
COPY database.py .

# Create cache directory for landing pages
RUN mkdir -p /app/cache

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=server.py

# Run with gunicorn in production
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "server:app"]
