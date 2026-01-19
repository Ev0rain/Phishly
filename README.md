<div align="center">

# 🐟 Phishly

### Phishing Simulation Platform for Security Awareness Training

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/flask-3.0.0-black.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker)](https://www.docker.com)

**Phishly** is a phishing simulation platform for organizations to conduct security awareness training and analyze employee behavior through controlled phishing campaigns.

[Quick Start](#quick-start) • [Architecture](#architecture) • [Team](#team)

</div>

---

## Current Features

- **Admin Dashboard** - Modern web interface with dark/light theme support
- **Campaign Management** - Create and track phishing campaigns with real-time statistics
- **Email Templates** - Pre-built templates (CEO Compromise, Password Reset, Invoice Request)
- **Target Groups** - Organize and manage employee target lists
- **Analytics & Insights** - Interactive charts and performance metrics
- **Settings Panel** - Theme customization and user preferences

---

## Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/) (20.10+) and [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)
- [Python](https://www.python.org/downloads/) 3.11 or higher
- Access to an SMTP service (Mailjet, Mailgun, SendGrid, etc.)
- Valid domain names for public and internal access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/phishly/phishly.git
   cd phishly
   ```

2. **One-Command Deployment** (Recommended)
   ```bash
   ./docker_phishly-deploy.sh
   ```

   This will automatically:
   - Start all Docker services
   - Create database schema
   - Create admin user (admin/admin123)
   - Configure everything (~2 minutes)

3. **Access the WebAdmin**
   - URL: http://localhost:8006
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ Change password after first login!

### After Reboot / Quick Restart

```bash
./docker_phishly-up.sh  # Restarts services, preserves data (~30 sec)
```

### Shutdown Services

```bash
./docker_phishly-down.sh  # Stops all services, preserves data
```

### Manual Configuration (Optional)

2. **Configure environment variables manually**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the platform**
   - **Admin Dashboard:** `http://localhost:8006` (development) or `https://admin.internal.example:8006` (production)
   - **Phishing Pages:** `https://phishing.example.com` (production only)

### Development Setup

For local development without Docker:

```powershell
# Windows PowerShell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
cd webadmin
pip install -r requirements.txt

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Create .env file (or use auto-generated key in dev mode)
# Copy the generated key to .env file

# Run development server
python app.py
# Access at http://localhost:8006
```

```bash
# Linux/macOS
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
cd webadmin
pip install -r requirements.txt

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Run development server
python app.py
```

---

## Configuration

### Environment Setup

The `.env` file contains all configuration variables:

```env
# Flask Configuration
SECRET_KEY=your-64-character-hex-string-here
FLASK_DEBUG=True

# Database (PostgreSQL)
POSTGRES_DB=phishly
POSTGRES_USER=phishly_user
POSTGRES_PASSWORD=your-secure-password-here
DATABASE_URL=postgresql://phishly_user:password@postgres-db:5432/phishly

# Redis (Session Storage & Message Queue)
REDIS_URL=redis://redis-cache:6379/0

# SMTP Configuration
SMTP_MOCK=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false

# Phishing Domain
PHISHING_DOMAIN=phishing.example.com
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key (64-char hex) | Auto-generated in dev | ✓ |
| `FLASK_DEBUG` | Enable debug mode | `True` | - |
| `DATABASE_URL` | PostgreSQL connection string | - | ✓ |
| `REDIS_URL` | Redis connection string | `redis://redis-cache:6379/0` | ✓ |
| `SMTP_MOCK` | Mock email sending (dev mode) | `true` | - |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` | ✓ |
| `SMTP_PORT` | SMTP server port | `587` | ✓ |
| `SMTP_USER` | SMTP authentication username | - | ✓ |
| `SMTP_PASSWORD` | SMTP authentication password | - | ✓ |
| `SMTP_USE_TLS` | Use TLS encryption | `true` | - |
| `PHISHING_DOMAIN` | Public-facing phishing domain | - | ✓ |

---

## Architecture

Phishly follows a **microservices architecture** with strict service boundaries:

```
                                ┌─────────────────────────────────────────────────────────────┐
                                │                    Caddy Reverse Proxy                      │
                                │          (HTTPS Termination & Request Routing)              │
                                └─────────────┬───────────────────────────┬───────────────────┘
                                              │                           │
                                    ┌─────────▼──────────┐       ┌────────▼─────────┐
                                    │   Webadmin Service │       │   Phish Service  │
                                    │   (Flask Admin)    │       │  (Landing Pages) │
                                    │   Port: 8006       │       │   (In Progress)  │
                                    └─────────┬──────────┘       └────────┬─────────┘
                                              │                           │
                                              └───────────┬───────────────┘
                                                          │
                                              ┌───────────▼────────────┐
                                              │   PostgreSQL Database  │
                                              │   Port: 5432           │
                                              └───────────┬────────────┘
                                                          │
                                    ┌─────────────────────┴─────────────────────┐
                                    │                                           │
                                ┌───▼──────────┐                    ┌───────────▼────────┐
                                │ Redis Queue  │◄───────────────────┤  Celery Worker     │
                                │ Port: 6379   │                    │  (Email Sending)   │
                                └──────────────┘                    └────────────────────┘
```

### Services

| Service | Technology | Purpose | Port |
|---------|-----------|---------|------|
| **webadmin** | Flask 3.0 | Admin dashboard & REST API | 8006 |
| **phish** | Flask 3.0 | Public phishing landing pages | (planned) |
| **worker** | Celery | Async task processing (emails) | - |
| **db** | PostgreSQL 17 | Data persistence | 5432 |
| **redis** | Redis 7 | Message queue & session storage | 6379 |
| **reverse-proxy** | Caddy 2 | HTTPS termination & routing | 80/443 |

### Network Isolation

**Two-domain architecture** ensures security:

- **Public Domain** (`phishing.example.com`)
  - Accessible from internet
  - Hosts phishing landing pages
  - Tracks user interactions
  - Isolated from admin panel

- **Internal Domain** (`admin.internal.example`)
  - Accessible only via company LAN/VPN
  - Admin dashboard and API
  - Campaign management
  - Statistics and reporting

The reverse proxy enforces this boundary. Admin endpoints are **never** exposed publicly.

---

## Security

### Authentication
- Session-based authentication (planned with Redis backend)
- Password hashing using werkzeug (PBKDF2-SHA256)
- HttpOnly, Secure, and SameSite cookie flags
- 2-hour session timeout (planned)

### Protection Mechanisms
- CSRF protection ready (Flask-WTF integration planned)
- Rate limiting on login endpoints (planned)
- SQL injection prevention (SQLAlchemy ORM ready)
- XSS protection via Jinja2 auto-escaping
- Input validation and sanitization

### Best Practices
- Environment-based secrets management
- No hardcoded credentials in codebase
- Principle of least privilege for services
- Regular security audits and updates

---

## Testing

Run the test suite:

```bash
# Run all tests
docker-compose exec webadmin pytest tests/

# Run specific test file
docker-compose exec webadmin pytest tests/test_campaigns.py

# Run with coverage
docker-compose exec webadmin pytest --cov=app tests/
```

---

## Team

| Member | Role | Responsibilities |
|--------|------|------------------|
| **Liam Wolff** | Project Lead | Project Management, Webadmin Development |
| **Diogo Carvalho** | Full-stack Developer | Database Architecture, Backend Support |
| **Sam Kafai** | Backend Developer | Worker Service, Redis Integration |
| **Sam Schroeder** | Database Engineer | Database Operations, Schema Design |
| **Rodrigo Sá** | Frontend Developer | Phishing Pages, Email Templates |

---

## License

This project is licensed under the **AGPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

---

## Legal Disclaimer

**IMPORTANT:** This tool is designed exclusively for **authorized security awareness training** within organizations. 

- [ ✓ ] Use only with explicit written authorization
- [ ✓ ] For educational and security training purposes only
- [ X ] Do **NOT** use for real phishing attacks
- [ X ] Do **NOT** use outside authorized campaigns
- [ X ] Unauthorized use may violate laws and regulations

Phishly is intended for legitimate cybersecurity training and awareness programs. Misuse of this software for malicious purposes is strictly prohibited and may result in criminal prosecution.

---

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Powered by [Celery](https://docs.celeryproject.org/)
- Secured with [Caddy](https://caddyserver.com/)

### Sponsors

Special thanks to **Lycée Guillaume Kroll (LGK)** for their support and resources that made this project possible.

---

## Support

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/phishly/phishly/issues)
- **Email:** phishly-team@example.com

---

<div align="center">

**[⬆ back to top](#-phishly)**

Made with ❤️ by the LuxGuard Team • © 2025 Phishly Project

</div>


