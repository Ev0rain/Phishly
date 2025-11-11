# 🐟 Phishly

Phishly is a **phishing simulation platform** designed for companies and institutions to **test employee awareness** and **analyze security behavior** through controlled phishing campaigns.

---

## 🚀 Overview
Phishly allows administrators to:
- Create and manage phishing campaigns
- Send customizable email templates
- Track opens, clicks, and submissions
- View campaign statistics via a web admin panel

The system runs in Docker containers for easy deployment and separation of services.

---

## 🧱 Architecture
Main components:
- **webadmin** – Flask-based admin dashboard & API  
- **phish** – Flask phishing landing pages  
- **worker** – Celery worker for sending emails and handling async tasks  
- **redis** – Message queue for Celery  
- **db** – PostgreSQL database for persistence  
- **reverse-proxy** – Caddy for HTTPS and internal routing  

---

## 🌐 Network Setup
- **Public phishing domain:** `phishing.example.com` → used for public-facing landing pages  
- **Internal admin domain:** `admin.internal.example` (or `admin.example.local`) → accessible only via company LAN / VPN  
- Reverse proxy decides routing and enforces access controls (public vs internal).

---

## ⚙️ Getting Started
### Prerequisites
- Docker & Docker Compose installed  
- A `.env` file with environment variables (see `.env.template`)  
- Access to an SMTP service (Mailjet, Mailgun, etc.)

### Run the stack
```bash
docker-compose up -d
```

Access:
- **Admin GUI:** `https://admin.internal.example:8006` (internal-only)  
- **Phishing landing page:** `https://phishing.example.com`

---

## 👥 Team
| Member | Role |
|--------|------|
| Liam Wolff | Project Management, Webadmin |
| Diogo Carvalho | Database, Full-stack Support |
| Sam Kafai | Worker & Redis |
| Sam Schroeder | Database |
| Rodrigo Sá | Phishing Landing Page & Templates |

---

## 🧾 License
Internal academic project for educational purposes only.  
**Do not use for real phishing outside of authorized awareness campaigns.**

---

*© 2025 Phishly Team — Lycée Guillaume Kroll (BTS Cybersecurity Project)*
