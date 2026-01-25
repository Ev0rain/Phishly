# Phishly WebAdmin - Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Base Python image with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Development image
FROM base as development

# Install gosu for dropping privileges
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create app user (same UID as host user for bind mount compatibility)
RUN useradd -m -u 1000 phishly

# Copy application code
COPY . .

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create writable directories with correct ownership
RUN mkdir -p /app/dns_zones /app/shared_cache /app/campaign_landing_pages \
    && chown -R phishly:phishly /app

# Expose port
EXPOSE 8006

# Entrypoint handles permission fixing and drops to app user
ENTRYPOINT ["docker-entrypoint.sh"]

# Run Flask development server
CMD ["python", "app.py"]

# Stage 3: Production image
FROM base as production

# Install gosu for dropping privileges
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies including production server
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn==21.2.0

# Create non-root user for security
RUN useradd -m -u 1000 phishly && \
    chown -R phishly:phishly /app

# Copy application code
COPY --chown=phishly:phishly . .

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create writable directories with correct ownership
RUN mkdir -p /app/dns_zones /app/shared_cache /app/campaign_landing_pages \
    && chown -R phishly:phishly /app

# Expose port
EXPOSE 8006

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8006/health').read()" || exit 1

# Entrypoint handles permission fixing and drops to app user
ENTRYPOINT ["docker-entrypoint.sh"]

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8006", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:create_app()"]
