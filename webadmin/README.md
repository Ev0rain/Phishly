# Phishly WebAdmin - Docker Setup

This directory contains the Flask-based admin dashboard for Phishly.

## Quick Start

### Development Mode (Local)

```powershell
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

Visit: http://localhost:8006

### Development Mode (Docker)

```powershell
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f webadmin

# Stop container
docker-compose down
```

Visit: http://localhost:8006

## Docker Commands

### Build Image
```powershell
# Development build
docker build --target development -t phishly-webadmin:dev .

# Production build
docker build --target production -t phishly-webadmin:prod .
```

### Run Container
```powershell
# Development mode
docker run -d -p 8006:8006 --name phishly-webadmin phishly-webadmin:dev

# Production mode
docker run -d -p 8006:8006 --name phishly-webadmin phishly-webadmin:prod
```

### Manage Containers
```powershell
# View logs
docker logs -f phishly-webadmin

# Access container shell
docker exec -it phishly-webadmin /bin/bash

# Restart container
docker restart phishly-webadmin

# Stop and remove
docker stop phishly-webadmin
docker rm phishly-webadmin
```

## Environment Configuration

Copy `.env.template` to `.env` and update values:

```powershell
cp .env.template .env
```

Required variables:
- `SECRET_KEY` - Flask session secret (change in production!)
- `FLASK_DEBUG` - Set to `False` in production
- `FLASK_PORT` - Port to run on (default: 8006)

Optional (when services are ready):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SMTP_*` - Email configuration

## Project Structure

```
webadmin/
├── app.py                  # Flask application factory
├── requirements.txt        # Python dependencies
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Container orchestration
├── .dockerignore          # Files to exclude from image
├── .env.template          # Environment variables template
├── routes/                # Flask blueprints
│   ├── auth.py           # Authentication (login/logout)
│   ├── dashboard.py      # Main dashboard
│   └── about.py          # About page
├── templates/             # Jinja2 HTML templates
│   ├── login.html
│   ├── dashboard.html
│   └── about.html
├── static/                # CSS, JS, images
│   ├── css/
│   │   ├── login.css
│   │   └── dashboard.css
│   └── js/
│       ├── login.js
│       └── dashboard.js
└── repositories/          # Data access layer (mock implementations)
    └── campaign_repository.py
```

## Health Check

The service includes a health check endpoint:

```powershell
# Check if service is running
curl http://localhost:8006/health

# Response
{
  "status": "healthy",
  "service": "webadmin"
}
```

## Production Deployment

For production, use the production Docker target with Gunicorn:

```powershell
# Build production image
docker build --target production -t phishly-webadmin:prod .

# Run with production settings
docker run -d \
  -p 8006:8006 \
  -e FLASK_DEBUG=False \
  -e SECRET_KEY=your-production-secret \
  --name phishly-webadmin \
  phishly-webadmin:prod
```

## Notes

- Database and Redis are not yet integrated (using mock data)
- Authentication is frontend-only (no backend validation yet)
- SMTP configuration is prepared but not implemented
- Health checks are configured for monitoring
