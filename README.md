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

- **Admin Dashboard** - Web interface for campaign management and statistics
- **Template System** - Create phishing email templates (in development)
- **Campaign Management** - Organize and track phishing campaigns (in development)
- **Authentication Ready** - Session-based auth infrastructure planned

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

2. **Configure environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the platform**
   - **Admin Dashboard:** `https://admin.internal.example:8006` (internal network only)
   - **Phishing Pages:** `https://phishing.example.com` (public-facing)

### Development Setup

For local development without Docker:

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run development server
cd webadmin
python app.py
```

---

## Configuration

### Environment Setup

The `.env` file contains all configuration variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
FLASK_PORT=8006

# Database
DATABASE_URL=postgresql://user:password@db:5432/phishly_db

# Redis
REDIS_URL=redis://redis:6379/0

# SMTP Configuration
SMTP_HOST=smtp.mailjet.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password

# Domains
PUBLIC_DOMAIN=phishing.example.com
ADMIN_DOMAIN=admin.internal.example
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for sessions | - | ✓ |
| `DATABASE_URL` | PostgreSQL connection string | - | ✓ |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | ✓ |
| `SMTP_HOST` | SMTP server hostname | - | ✓ |
| `SMTP_PORT` | SMTP server port | `587` | ✓ |
| `SMTP_USERNAME` | SMTP authentication username | - | ✓ |
| `SMTP_PASSWORD` | SMTP authentication password | - | ✓ |
| `PUBLIC_DOMAIN` | Public-facing phishing domain | - | ✓ |
| `ADMIN_DOMAIN` | Internal admin panel domain | - | ✓ |

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
                                    │   Port: 8006       │       │   Port: 8007     │
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
| **phish** | Flask 3.0 | Public phishing landing pages | 8007 |
| **worker** | Celery | Async task processing (emails) | - |
| **db** | PostgreSQL 15 | Data persistence | 5432 |
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
- Session-based authentication with Redis backend
- Password hashing using werkzeug (PBKDF2-SHA256)
- HttpOnly, Secure, and SameSite cookie flags
- 2-hour session timeout

### Protection Mechanisms
- CSRF protection on all forms (Flask-WTF)
- Rate limiting on login endpoints
- SQL injection prevention (SQLAlchemy ORM)
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
