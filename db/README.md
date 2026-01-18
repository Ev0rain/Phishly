# Phishly Database - PostgreSQL Configuration

# ============================================
# Notes
# ============================================
# The database service runs in a Docker container
# using the official PostgreSQL image.
# 
# No Python dependencies are needed here.
# The database is accessed via psycopg2 from
# webadmin and worker services.
#
# Database schema and migrations are managed
# by the webadmin service using Alembic.

# ============================================
# Docker Image Used
# ============================================
# postgres:16-alpine

# ============================================
# Connection Details
# ============================================
# Host: db (in Docker network) or localhost (local dev)
# Port: 5432
# Database: phishly_db
# User: phishly_user
# Password: Set via POSTGRES_PASSWORD environment variable
