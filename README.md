<div align="center">

# 🐟 Phishly

### Phishing Simulation Platform for Security Awareness Training

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/flask-3.0.0-black.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker)](https://www.docker.com)
[![Podman](https://img.shields.io/badge/podman-ready-892CA0.svg?logo=podman)](https://podman.io)

**Phishly** is a phishing simulation platform for organizations to conduct security awareness training and analyze employee behavior through controlled phishing campaigns.

[Quick Start](#quick-start) • [Deployment](#deployment) • [Templates](#template-management) • [Architecture](#architecture) • [Tracking](#how-tracking-works) • [Team](#team)

</div>

---

## Current Features

- **Admin Dashboard** - Modern web interface with dark/light theme support
- **Campaign Management** - Create and track phishing campaigns with real-time statistics
- **Email Templates** - Pre-built templates (CEO Compromise, Password Reset, Invoice Request)
- **Target Groups** - Organize and manage employee target lists
- **Landing Pages** - Customizable phishing landing pages with domain configuration
- **Email Tracking** - Track opens, clicks, and form submissions with unique tokens
- **Analytics & Insights** - Interactive charts and performance metrics
- **Settings Panel** - Theme customization and user preferences

---

## Quick Start

### Prerequisites

Choose your container runtime:

**Option A: Docker** (Recommended for most users)
- [Docker](https://docs.docker.com/get-docker/) (20.10+) and [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)

**Option B: Podman** (Enhanced security, rootless)
- [Podman](https://podman.io/getting-started/installation) (4.0+)
- [Podman Compose](https://github.com/containers/podman-compose) (`pip install podman-compose`)

**Additional Requirements:**
- [Python](https://www.python.org/downloads/) 3.11 or higher
- Access to an SMTP service (Mailjet, Mailgun, SendGrid, etc.)
- Valid domain names for phishing landing pages

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ev0rain/Phishly.git
   cd phishly
   ```

2. **One-Command Deployment**

   **Using Docker:**
   ```bash
   ./docker_phishly-deploy.sh
   ```

   **Using Podman:**
   ```bash
   ./podman_phishly-deploy.sh
   ```

   This will automatically:
   - Start all services
   - Create database schema
   - Create admin user (admin/admin123)
   - Configure everything (~2 minutes)

3. **Access the WebAdmin**
   - URL: http://localhost:8006
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ **Change password after first login!**

### Quick Commands

| Action | Docker | Podman |
|--------|--------|--------|
| **First setup** | `./docker_phishly-deploy.sh` | `./podman_phishly-deploy.sh` |
| **After reboot** | `./docker_phishly-up.sh` | `./podman_phishly-up.sh` |
| **Restart services** | `./docker_phishly-restart.sh` | `./podman_phishly-restart.sh` |
| **Stop services** | `./docker_phishly-down.sh` | `./podman_phishly-down.sh` |

---

## Deployment

### Prerequisites

#### One-Time Directory Setup

Before first deployment, you may need to fix directory ownership if any directories were previously created as root:

```bash
# Check if directories need fixing
ls -la webadmin/email_templates_imported webadmin/dns_zones

# If any show "root" as owner, run the fix script:
sudo ./fix_directory_ownership.sh
```

This ensures containers running as non-root users (UID 1000) can write to required directories.

**Note:** This is only needed once, or if you manually created directories as root. Normal deployments handle directory creation automatically.

### Deployment Scripts

Phishly includes automated deployment scripts for both Docker and Podman:

#### 1. Full Deployment (`*-deploy.sh`)
**Use for:** First-time setup or complete redeployment

**What it does:**
- Checks container runtime installation
- Starts all services
- Creates database schema
- Creates admin user (admin/admin123)
- Runs health checks
- Full initialization (~2 minutes)

**Usage:**
```bash
# Docker
./docker_phishly-deploy.sh

# Podman
./podman_phishly-deploy.sh
```

#### 2. Quick Start/Restart (`*-up.sh`)
**Use for:** After reboot, code updates, or service restart

**What it does:**
- Starts/restarts all services
- Preserves all data
- No database re-initialization
- Quick startup (~30 seconds)

**Usage:**
```bash
# Docker
./docker_phishly-up.sh

# Podman
./podman_phishly-up.sh
```

#### 3. Graceful Shutdown (`*-down.sh`)
**Use for:** Shutting down for maintenance or system shutdown

**What it does:**
- Stops all containers gracefully
- Preserves all data and volumes
- Keeps container images cached
- Clean shutdown (~15 seconds)

**Usage:**
```bash
# Docker
./docker_phishly-down.sh

# Podman
./podman_phishly-down.sh
```

#### 4. Quick Restart (`*-restart.sh`)
**Use for:** Restarting services after configuration changes

**What it does:**
- Restarts all containers in-place
- Fastest restart method
- Preserves all state (~10 seconds)

**Usage:**
```bash
# Docker
./docker_phishly-restart.sh

# Podman
./podman_phishly-restart.sh
```

### Podman-Specific Configuration

#### Security Note
Podman-compose may display configuration file contents (including credentials) in terminal output. All Podman scripts use output redirection to prevent credential exposure.

#### Recommended Aliases
Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Podman Compose aliases (suppress output to prevent credential exposure)
alias pcup='podman-compose up -d >/dev/null 2>&1'
alias pcdown='podman-compose down >/dev/null 2>&1'
alias pcrestart='podman-compose restart >/dev/null 2>&1'
alias pcps='podman-compose ps'
alias pclogs='podman logs -f'
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

#### Rootless Podman Setup (Optional)

For enhanced security, run Podman as a non-root user:

```bash
# Create podman user
sudo useradd -m -s /bin/bash podman
sudo usermod -aG podman podman

# Configure subuid/subgid
echo "podman:100000:65536" | sudo tee -a /etc/subuid
echo "podman:100000:65536" | sudo tee -a /etc/subgid

# Switch to podman user
sudo su - podman
cd /path/to/Phishly

# Deploy
./podman_phishly-deploy.sh
```

### Manual Deployment (Advanced)

If you prefer manual control:

1. **Configure environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

2. **Start services**
   ```bash
   # Docker
   docker-compose up -d

   # Podman (with output suppression)
   podman-compose up -d >/dev/null 2>&1
   ```

3. **Initialize database** (first-time only)
   ```bash
   # Docker
   docker exec phishly-webadmin python init_db.py

   # Podman
   podman exec phishly-webadmin python init_db.py
   ```

4. **Access the platform**
   - **Admin Dashboard:** http://localhost:8006

### Useful Commands

#### Docker

```bash
# View service status
docker-compose ps

# View logs
docker logs -f phishly-webadmin
docker logs -f celery-worker

# Execute command in container
docker exec -it phishly-webadmin bash

# Check resource usage
docker stats

# Clean up unused images
docker image prune -a
```

#### Podman

```bash
# View service status
podman-compose ps

# View logs
podman logs -f phishly-webadmin
podman logs -f celery-worker

# Execute command in container
podman exec -it phishly-webadmin bash

# Check resource usage
podman stats

# Clean up unused images
podman image prune -a
```

---

## Configuration

### Environment Setup

The `.env` file contains all configuration variables. Create from template:

```bash
cp .env.template .env
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| **Flask Configuration** |
| `SECRET_KEY` | Flask secret key (64-char hex) | Auto-generated in dev | ✓ |
| `FLASK_DEBUG` | Enable debug mode | `True` | - |
| `FLASK_PORT` | WebAdmin port | `8006` | - |
| **Database (PostgreSQL)** |
| `POSTGRES_HOST` | Database host | `postgres-db` | ✓ |
| `POSTGRES_PORT` | Database port | `5432` | - |
| `POSTGRES_DB` | Database name | `phishly` | ✓ |
| `POSTGRES_USER` | Database user | `phishly_user` | ✓ |
| `POSTGRES_PASSWORD` | Database password | - | ✓ |
| `DATABASE_URL` | Full PostgreSQL connection string | - | ✓ |
| **Cache & Queue (Redis)** |
| `REDIS_HOST` | Redis host | `redis-cache` | ✓ |
| `REDIS_PORT` | Redis port | `6379` | - |
| `REDIS_URL` | Full Redis URL for sessions | - | ✓ |
| **Email (SMTP)** |
| `SMTP_MOCK` | Mock email sending (dev mode) | `true` | - |
| `SMTP_HOST` | SMTP server hostname | - | ✓ |
| `SMTP_PORT` | SMTP server port (587/465) | `587` | ✓ |
| `SMTP_USER` | SMTP authentication username | - | ✓ |
| `SMTP_PASSWORD` | SMTP authentication password | - | ✓ |
| `SMTP_USE_TLS` | Use TLS encryption | `true` | - |
| `SMTP_USE_SSL` | Use SSL encryption | `false` | - |
| **Phishing** |
| `PHISHING_DOMAIN` | Fallback phishing domain | `localhost` | - |

**Note:** Individual landing pages have their own domain configuration (mandatory) which overrides `PHISHING_DOMAIN` for email links.

### Example Configuration

```env
# Flask
SECRET_KEY=your-64-character-hex-string-here
FLASK_DEBUG=False
FLASK_PORT=8006

# Database
POSTGRES_DB=phishly
POSTGRES_USER=phishly_user
POSTGRES_PASSWORD=your-secure-password-here
DATABASE_URL=postgresql://phishly_user:password@postgres-db:5432/phishly

# Redis
REDIS_URL=redis://redis-cache:6379/0

# SMTP (Mailjet example)
SMTP_MOCK=false
SMTP_HOST=in-v3.mailjet.com
SMTP_PORT=587
SMTP_USER=your-mailjet-api-key
SMTP_PASSWORD=your-mailjet-secret-key
SMTP_USE_TLS=true
SMTP_USE_SSL=false

# Phishing (fallback domain)
PHISHING_DOMAIN=phishing.example.com
```

---

## Template Management

### Email Templates

Email templates define the content of phishing emails sent to targets.

#### Storage System

**Database Storage** (Complete Template):
- Full template stored in PostgreSQL `email_templates` table
- Includes: metadata (name, subject, sender) + HTML content
- Templates are independent of source files after import
- Ensures templates remain available regardless of file system changes

**Template Library** (Source Templates):
- Location: `/templates/email_templates/`
- Pre-built HTML templates ready to import
- Read-only source files, not modified by system
- Not tracked in git (contains sensitive phishing content)

#### How Email Templates Work

1. **Before Import**: Templates exist as `.html` files in `/templates/email_templates/`
2. **Import Process**: When you create a template in WebAdmin:
   - HTML content is read from source file
   - Complete template (metadata + HTML) is saved to database
   - Template becomes independent of source file
3. **After Import**: Template lives entirely in database
4. **Deletion**: Removing template in WebAdmin deletes it from database only

#### Importing Email Templates

1. **Add source template to library**:
   ```bash
   # Add your template HTML file to the library
   cp my_phishing_template.html /templates/email_templates/
   ```

2. **Import via WebAdmin**:
   - Navigate to **Templates** page
   - Click "Import Template"
   - Select template file from dropdown
   - Configure metadata:
     - Template name
     - Email subject line
     - Sender email and name
     - Default landing page (optional)
   - Click "Import"

3. **What happens**:
   - HTML content read from `/templates/email_templates/{filename}`
   - Complete template saved to database (`email_templates.body_html`)
   - Source file in `/templates` remains unchanged
   - Template immediately available for campaigns

#### Template Variables

Email templates use **Jinja2 syntax** (`{{ variable_name }}`) for personalization. All variables are substituted at send time by the Celery worker.

**Target Information**:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ salutation }}` | Target's salutation (Mr., Ms., Dr., etc.) | `Mr.` |
| `{{ first_name }}` | Target's first name | `John` |
| `{{ last_name }}` | Target's last name | `Smith` |
| `{{ email }}` | Target's email address | `john.smith@company.com` |
| `{{ position }}` | Target's job title | `IT Manager` |
| `{{ department }}` | Target's department | `Engineering` |

**Sender Information** (from the email template metadata):

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ sender_name }}` | Sender display name | `IT Support` |
| `{{ sender_email }}` | Sender email address | `support@company.com` |
| `{{ from_name }}` | Alias for `sender_name` | `IT Support` |
| `{{ from_email }}` | Alias for `sender_email` | `support@company.com` |

**Campaign Information**:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ campaign_name }}` | Name of the campaign | `Q1 Security Awareness` |

**Tracking & Links** (auto-generated):

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ phishing_link }}` | Full URL to landing page with tracking token | `https://domain.com/login?t=abc123` |
| `{{ landing_page_url }}` | Alias for `phishing_link` | `https://domain.com/login?t=abc123` |
| `{{ tracking_pixel_url }}` | URL for the open-tracking pixel | `https://domain.com/track/open?t=abc123` |
| `{{ unsubscribe_url }}` | Unsubscribe link URL | `https://domain.com/unsubscribe?t=abc123` |

**Auto-generated Utility Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ tracking_number }}` | UPS-style tracking number (for shipping templates) | `1Z999AA10123456784` |
| `{{ delivery_date }}` | Date 3–5 days in the future | `January 31, 2026` |
| `{{ year }}` | Current year (for copyright footers) | `2026` |

**Example template**:
```html
<!DOCTYPE html>
<html>
<body>
    <p>Dear {{ salutation }} {{ last_name }},</p>
    <p>The {{ department }} department requires your immediate attention.</p>
    <p>Please <a href="{{ phishing_link }}">click here to verify your account</a>.</p>
    <p>If you have questions, contact us at {{ sender_email }}</p>
    <p>&copy; {{ year }} {{ sender_name }}. All rights reserved.</p>
</body>
</html>
```

**Subject line**: The email subject also supports Jinja2 variables. For example:
```
Urgent: {{ first_name }}, your account requires verification
```

#### Authoring Guidelines for Email Templates

**HTML Structure Requirements**

- Your HTML **must** include a `</body>` tag. The tracking pixel is automatically injected immediately before `</body>`. If no `</body>` tag is found, the pixel is appended to the end of the HTML, which may not render correctly in all email clients.
- Use a complete HTML structure (`<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`) for best compatibility.

**Phishing Link Placement**

Use the `{{ phishing_link }}` variable for all links that should direct targets to the landing page:
```html
<a href="{{ phishing_link }}">Click here to take action</a>
```

This variable expands to the full URL including the tracking token: `https://{landing_page_domain}/{url_path}?t={token}`. The domain and path come from the landing page assigned to the campaign.

**Do not** manually construct tracking URLs or hardcode domains in your template — always use the provided variables.

**Email Client Compatibility**

For broad email client support:
- Use **inline CSS** styles rather than `<style>` blocks (many email clients strip `<style>` tags)
- Use **table-based layouts** for consistent rendering across Outlook, Gmail, Apple Mail, etc.
- Avoid JavaScript — it is blocked by all major email clients
- Use absolute URLs for any images (relative paths will not work in email)
- Keep total email size under 100 KB for deliverability

**Plain Text Fallback**

If the template does not provide a `body_text` field, a plain text version is automatically generated by stripping HTML tags from the rendered HTML. For better control over the plain text version, provide it explicitly.

**What Not to Include**

- Do **not** add a tracking pixel manually — it is injected automatically
- Do **not** include the `{{ tracking_token }}` variable directly in email body text — use `{{ phishing_link }}` instead, which already embeds the token
- Do **not** hardcode the phishing domain — it is resolved from the landing page configuration

#### Editing Templates

- **Metadata**: Use WebAdmin "Edit" button to change:
  - Template name
  - Email subject
  - Sender email and name
  - Default landing page assignment
- **HTML Content**: Cannot be edited after import
  - To change HTML, create new template from updated source file
  - Or directly update `email_templates.body_html` in database

**Note**: Changes to metadata apply to future campaigns. Existing campaigns use the original settings.

### Landing Pages

Landing pages are the web pages targets see after clicking phishing links. They can capture credentials, form data, and track interactions.

#### Storage System

**Database Storage** (Metadata):
- Page name, URL path, domain
- Form configuration (capture settings)
- Template path reference
- Stored in PostgreSQL `landing_pages` table

**File Storage** (Template-based):
- Location: `templates/landing_pages/{template_name}/`
- Each template is a complete web application
- Contains HTML, CSS, JavaScript, images

**Deployment** (Runtime):
- Templates deployed to `server/landing_pages_deployed/{campaign_id}/`
- Each campaign gets isolated copy
- Allows per-campaign customization

#### Template Structure

A landing page template directory contains:

```
templates/landing_pages/my-template/
├── index.html          # Main page (required)
├── success.html        # Post-submission page (optional)
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── logo.png
└── forms/
    └── login-form.json # Form configuration (optional)
```

#### Creating Landing Pages

**Option 1: Import from Template Library**

1. **Add template to library**:
   ```bash
   # Create directory structure
   mkdir -p templates/landing_pages/my-template/static/{css,js,images}

   # Add your HTML, CSS, JS files
   cp index.html templates/landing_pages/my-template/
   ```

2. **Import via WebAdmin**:
   - Navigate to **Landing Pages**
   - Click "Create Landing Page"
   - Select template from dropdown
   - Configure:
     - **Name**: Display name
     - **URL Path**: e.g., `/login` or `/verify`
     - **Domain**: e.g., `phishing.example.com` (required)
     - **Capture Settings**: Enable credential/form capture
   - Click "Create"

**Option 2: Legacy Database Storage**

Upload HTML/CSS/JS directly via WebAdmin (older method, not recommended for complex pages)

#### Domain Configuration

**IMPORTANT**: Each landing page **must** have a domain configured:

- Domain used for generating email tracking links
- Overrides global `PHISHING_DOMAIN` setting
- Format: `phishing.example.com` (no protocol)
- Must be accessible from internet for target access

**Example**:
- Landing page domain: `ups-be.com`
- Email links generated: `https://ups-be.com/verify?t={token}`
- Preview (webadmin): `http://localhost:8006/phishing-preview/`

#### Template Variables (Landing Pages)

Landing page HTML templates support these variables:

```html
<!-- Tracking -->
{{ tracking_token }}      <!-- Unique token for this target -->
{{ campaign_id }}         <!-- Campaign identifier -->

<!-- Target Information (if passed) -->
{{ target_email }}        <!-- Pre-fill email field -->
{{ target_name }}         <!-- Personalization -->
```

#### Activation and Deployment

1. **Activate Landing Page**:
   - Only one landing page can be active at a time
   - Activation deploys template to phishing server
   - Makes page accessible at configured domain

2. **Campaign Deployment**:
   - Each campaign gets isolated template copy
   - Deployed to `server/landing_pages_deployed/{campaign_id}/`
   - Allows tracking per-campaign

3. **Deactivation**:
   - Stops serving landing page
   - Can only deactivate if no active campaigns use it
   - Cleans up deployed files

#### Authoring Guidelines for Landing Pages

To ensure tracking works correctly, landing page HTML must follow these rules:

**Form Submissions**

All forms must POST to `/api/submit` with the tracking token. There are two ways to include the token:

**Option A** — Query parameter (recommended):
```html
<form method="POST" action="/api/submit?t={{ tracking_token }}">
  <input type="email" name="email" placeholder="Email" />
  <input type="password" name="password" placeholder="Password" />
  <button type="submit">Sign In</button>
</form>
```

**Option B** — Hidden field:
```html
<form method="POST" action="/api/submit">
  <input type="hidden" name="_token" value="{{ tracking_token }}" />
  <input type="email" name="email" />
  <input type="password" name="password" />
  <button type="submit">Sign In</button>
</form>
```

If your landing page uses JavaScript to submit forms, make sure the tracking token is included in the POST request body or as a query parameter.

**Credential Detection**

The phishing server automatically detects password fields by checking for these field names: `password`, `passwd`, `pass`, `pwd`, `secret`. If any of these are present in the submitted form, the event is logged as `credentials_captured` instead of `form_submitted`. Name your password fields accordingly if you want this distinction.

**Reserved URL Paths**

Do **not** use these paths for your landing page content — they are reserved by the phishing server:

| Path | Purpose |
|------|---------|
| `/track/open` | Email open tracking pixel endpoint |
| `/api/submit` | Form submission endpoint |
| `/health` | Health check endpoint |
| `/awareness` | Awareness training redirect page |

**Static Assets**

Static files (CSS, JS, images, fonts) are served from your template directory without triggering tracking events. Supported extensions: `.css`, `.js`, `.png`, `.jpg`, `.gif`, `.svg`, `.ico`, `.woff`, `.woff2`, `.ttf`, `.eot`, `.map`.

Reference them with relative paths:
```html
<link rel="stylesheet" href="assets/css/style.css" />
<script src="assets/js/script.js"></script>
<img src="assets/images/logo.png" />
```

**Post-Submission Redirect**

Configure the `redirect_url` field on your landing page to control where targets go after submitting a form. Common patterns:
- Redirect to an awareness/training page (e.g., `https://your-domain.com/awareness`)
- Redirect to the real login page of the spoofed service
- Redirect to a "thank you" or "error" page within your template

**Multiple Pages**

A landing page template can contain multiple HTML files (e.g., `index.html`, `login.html`, `login-alt.html`). The phishing server resolves files in this order:
1. Exact file match (e.g., `/login.html` serves `login.html`)
2. Directory with `index.html` (e.g., `/` serves `index.html`)
3. Fallback to root `index.html`

---

## Target Management

### Target Database

Targets represent the individuals who will receive phishing emails. The target system supports individual management and group-based organization.

#### Target Information

Each target record contains:

| Field | Description | Required | Privacy Level |
|-------|-------------|----------|---------------|
| **email** | Email address | ✓ | High |
| **first_name** | First name | ✓ | Medium |
| **last_name** | Last name | ✓ | Medium |
| **position** | Job title | - | Low |
| **department** | Department name | - | Low |
| **notes** | Internal notes | - | Low |

#### Target Groups

Targets can be organized into groups for easier campaign management:

- **Group-based**: Create groups by department, location, role
- **CSV Import**: Bulk import targets from CSV files
- **Dynamic Assignment**: Assign targets to multiple groups
- **Campaign Selection**: Select entire groups for campaigns

**Creating Groups**:
1. Navigate to **Targets** page
2. Click "Create Group"
3. Add name and description
4. Select existing targets or import new ones via CSV

**CSV Import Format**:
```csv
email,first_name,last_name,position,department
john.doe@company.com,John,Doe,Manager,IT
jane.smith@company.com,Jane,Smith,Developer,Engineering
```

### Data Retention and Deletion

#### What Data is Stored

When a target is part of a campaign:

1. **Target Profile** (`targets` table):
   - Personal information (email, name, position, department)
   - Created timestamp
   - Notes

2. **Campaign Association** (`campaign_targets` table):
   - Link between target and campaign
   - Unique tracking token
   - Current status (pending, opened, clicked, submitted)
   - Created timestamp

3. **Email Jobs** (`email_jobs` table):
   - Email send status
   - Celery task ID
   - Send/delivery timestamps
   - Error messages (if failed)

4. **Events** (`events` table):
   - Email opens (timestamp, IP, user agent)
   - Link clicks (timestamp, IP, browser/OS/device)
   - Form submissions (timestamp, IP, device info)
   - Credential captures (if enabled)

5. **Form Submissions** (`form_submissions` + `form_answers` tables):
   - Complete form data
   - Field-level answers
   - Submission metadata

#### Target Deletion Process

**Standard Deletion** (Keep Campaign Data):

When you delete a target from the Targets page:

1. **Target Profile** → ✅ DELETED
2. **Campaign Associations** → ⚠️ ANONYMIZED
   - Target ID remains (for referential integrity)
   - Links to campaign data preserved
3. **Email Jobs** → ⚠️ RETAINED
   - Status history maintained
   - Used for campaign statistics
4. **Events** → ⚠️ RETAINED
   - Tracking events preserved
   - Enables analytics/reporting
5. **Form Submissions** → ⚠️ RETAINED
   - Captured data preserved
   - Used for training analysis

**Effect**: Target's personal info deleted, but campaign performance data remains for statistics.

**Privacy Deletion** (Complete Removal):

For GDPR/privacy compliance, use the "Privacy Delete" option:

1. **Target Profile** → ✅ DELETED
2. **Campaign Associations** → ✅ DELETED
3. **Email Jobs** → ✅ DELETED
4. **Events** → ✅ DELETED
5. **Form Submissions** → ✅ DELETED

**Effect**: ALL data related to the target is permanently removed. Campaign statistics will reflect reduced totals.

**Warning**: Privacy deletion cannot be undone and may affect historical campaign metrics.

#### Deletion Methods

**Via WebAdmin**:
```
Targets Page → Select Target → Delete Button → Confirm
- Standard Deletion: Click "Delete"
- Privacy Deletion: Click "Privacy Delete" (checkbox option)
```

**Via Database** (Manual):
```sql
-- Standard deletion (soft delete - keeps campaign data)
DELETE FROM targets WHERE id = {target_id};

-- Privacy deletion (complete removal - cascade delete)
DELETE FROM form_answers WHERE submission_id IN (
    SELECT id FROM form_submissions
    WHERE campaign_target_id IN (
        SELECT id FROM campaign_targets WHERE target_id = {target_id}
    )
);
DELETE FROM form_submissions WHERE campaign_target_id IN (
    SELECT id FROM campaign_targets WHERE target_id = {target_id}
);
DELETE FROM events WHERE campaign_target_id IN (
    SELECT id FROM campaign_targets WHERE target_id = {target_id}
);
DELETE FROM email_jobs WHERE campaign_target_id IN (
    SELECT id FROM campaign_targets WHERE target_id = {target_id}
);
DELETE FROM campaign_targets WHERE target_id = {target_id};
DELETE FROM targets WHERE id = {target_id};
```

#### Data Retention Policy

**Recommended Policies**:

1. **Active Campaigns**: Retain all data during campaign
2. **Completed Campaigns**:
   - Keep anonymized statistics (6-12 months)
   - Privacy delete individual targets on request
3. **Inactive Targets**: Delete after 12 months of no campaigns
4. **Form Data**: Review and delete sensitive captures regularly

**Compliance**:
- GDPR: Support privacy deletion (right to be forgotten)
- CCPA: Provide data export and deletion on request
- Internal Policies: Configure retention based on company requirements

#### Data Export

Before deletion, you can export target data:

```bash
# Export all targets
docker exec postgres-db psql -U phishly_user -d phishly \
  -c "COPY targets TO STDOUT CSV HEADER" > targets_export.csv

# Export campaign results for specific target
docker exec postgres-db psql -U phishly_user -d phishly \
  -c "SELECT * FROM events WHERE campaign_target_id IN (
        SELECT id FROM campaign_targets WHERE target_id = {target_id}
      )" > target_events.csv
```

---

## Architecture

Phishly follows a **microservices architecture** with six containers across three isolated networks:

```
                                ┌─────────────────────────────────────────────────────────────┐
                                │                    Caddy Reverse Proxy                      │
                                │          (HTTPS Termination & Request Routing)              │
                                │          Ports: 80, 443, 8006                               │
                                │          Networks: net_public, net_admin, net_data           │
                                └─────────────┬───────────────────────────┬───────────────────┘
                                              │                           │
                                    ┌─────────▼──────────┐       ┌────────▼─────────┐
                                    │   Webadmin Service │       │   Phish Service  │
                                    │   (Flask Admin)    │       │  (Landing Pages) │
                                    │   Port: 8006       │       │   Port: 8000     │
                                    │   net_admin,       │       │   net_public,    │
                                    │   net_data         │       │   net_data       │
                                    └─────────┬──────────┘       └────────┬─────────┘
                                              │                           │
                                              └───────────┬───────────────┘
                                                          │
                                              ┌───────────▼────────────┐
                                              │   PostgreSQL Database  │
                                              │   Port: 5432           │
                                              │   net_data             │
                                              └───────────┬────────────┘
                                                          │
                                    ┌─────────────────────┴─────────────────────┐
                                    │                                           │
                                ┌───▼──────────┐                    ┌───────────▼────────┐
                                │ Redis Cache  │◄───────────────────┤  Celery Worker     │
                                │ Port: 6379   │                    │  (Email Sending)   │
                                │ net_data     │                    │  net_data          │
                                └──────────────┘                    └────────────────────┘
```

### Services

| Service | Technology | Purpose | Port |
|---------|-----------|---------|------|
| **reverse-proxy** | Caddy 2 | HTTPS termination, routing, access control | 80/443/8006 |
| **webadmin** | Flask 3.0 | Admin dashboard, campaign management, REST API | 8006 |
| **phishing server** | Flask 3.0 | Public landing pages, tracking endpoints, form capture | 8000 |
| **worker** | Celery | Async email sending, campaign batch processing | — |
| **db** | PostgreSQL 17 | All persistent data (campaigns, targets, events, templates) | 5432 |
| **redis** | Redis 7 | Session storage, message broker, task results | 6379 |

### Container Roles

**Caddy Reverse Proxy** (`phishly-reverse-proxy`)
- Terminates TLS/SSL using mounted certificates
- Routes public traffic (ports 80/443) to the phishing server
- Routes admin traffic (port 8006) to the webadmin service
- Enforces access control: admin endpoints restricted to private networks (RFC 1918, IPv6 ULA, localhost) — never exposed publicly
- Forwards client IP addresses to backend services via `X-Forwarded-For`

**WebAdmin** (`phishly-webadmin`)
- Admin dashboard for creating and managing campaigns, targets, email templates, and landing pages
- Provides REST API for all management operations
- Handles user authentication with session-based login (sessions stored in Redis)
- Deploys landing page templates to campaign-specific directories on launch
- Runs database migrations and initialization on first deployment
- Uses a custom `docker-entrypoint.sh` that initializes directories and drops to a non-root user (UID 1000)

**Phishing Server** (`phishly-phishing`)
- Serves landing pages to targets who click phishing links
- Handles tracking endpoints: `/track/open` (email open pixel), link clicks (via `?t=` parameter), and `/api/submit` (form submissions)
- Resolves landing page content from campaign deployment directories, legacy cache, or database fallback
- Logs all tracking events (IP, user agent, browser, OS, device type) to the database
- Serves static assets (CSS, JS, images) without triggering tracking events
- Read-only access to campaign deployment volumes

**Celery Worker** (`celery-worker`)
- Processes email sending tasks asynchronously from the Redis queue
- Renders email templates with Jinja2 (substitutes target info, builds tracking URLs, injects tracking pixel)
- Sends emails via SMTP with configurable TLS/SSL
- Retries failed sends up to 3 times with 60-second delays
- Idempotent: checks if email already sent before retrying to prevent duplicates
- Task timeout: 5 minutes per email, prefetch multiplier of 1 (processes one task at a time)

**PostgreSQL** (`postgres-db`)
- Stores all persistent data: campaigns, targets, email templates, landing pages, tracking events, form submissions
- Health-checked with `pg_isready`
- Data persisted in `phishly_postgres_data` Docker volume

**Redis** (`redis-cache`)
- Uses three logical databases for separation of concerns:
  - **DB 0**: Flask session storage (webadmin login sessions)
  - **DB 1**: Celery message broker (task queue)
  - **DB 2**: Celery results backend (task status/results)
- Data persisted in `phishly_redis_data` Docker volume with AOF persistence

### Network Isolation

Phishly uses **three isolated Docker networks** to enforce strict service boundaries:

| Network | Containers | Purpose |
|---------|-----------|---------|
| `net_public` | reverse-proxy, phishing server | Internet-facing traffic (landing pages, tracking) |
| `net_admin` | reverse-proxy, webadmin | Admin access (restricted to LAN/VPN) |
| `net_data` | All services | Internal data plane (database, Redis, worker) |

**Two-domain architecture**:

- **Public Domain** (e.g., `phishing.example.com`)
  - Configured per landing page — each page specifies its own domain
  - Accessible from the internet via ports 80/443
  - Hosts phishing landing pages and tracking endpoints
  - Completely isolated from the admin panel

- **Internal Domain** (e.g., `admin.internal.example` or `localhost:8006`)
  - Accessible only via company LAN/VPN or localhost
  - Caddy rejects connections from public IP ranges
  - Hosts the admin dashboard, campaign management, and reporting

### Shared Volumes

| Volume | Mounted By | Purpose |
|--------|-----------|---------|
| `phishly_postgres_data` | db | PostgreSQL data persistence |
| `phishly_redis_data` | redis | Redis data persistence |
| Campaign deployments | webadmin (read-write), phishing server (read-only) | Landing pages deployed per-campaign at runtime |
| Template library | webadmin (read-only) | Source email and landing page templates |
| Legacy cache | webadmin (read-write), phishing server (read-only) | Backward-compatible landing page cache |

---

## How Tracking Works

Phishly tracks target interactions through a token-based system that follows each target across the full campaign lifecycle: email delivery, open detection, link clicks, and form submissions.

### Tracking Tokens

Each target in a campaign receives a **unique tracking token** — a deterministic identifier generated using HMAC-SHA256:

```
token = HMAC-SHA256(campaign_id + target_id, secret_key)  →  URL-safe base64, 32 characters
```

- Tokens are **deterministic**: the same campaign + target always produces the same token
- Tokens are stored in the `campaign_targets.tracking_token` column (unique constraint)
- Generated on first email send and reused for all subsequent interactions
- Tokens are embedded in email links and the tracking pixel URL

### Email Open Tracking

**Mechanism**: Invisible 1x1 transparent GIF pixel injected into every outgoing email.

**Flow**:
1. The Celery worker renders the email template and automatically injects a tracking pixel before the `</body>` tag:
   ```html
   <img src="https://{landing_page_domain}/track/open?t={tracking_token}"
        width="1" height="1" style="display:none;" />
   ```
2. When the target opens the email, their email client loads the pixel image
3. The phishing server receives the request at `/track/open?t={token}`
4. The server looks up the `campaign_target` by token and logs an `email_opened` event
5. The target's status is updated to `opened`

**Limitations**: Some email clients block external images by default, so open tracking may undercount actual opens.

### Link Click Tracking

**Mechanism**: Tracking token appended as a query parameter to all phishing links.

**Flow**:
1. The email template uses the `{{ phishing_link }}` variable, which renders as:
   ```
   https://{landing_page_domain}/{url_path}?t={tracking_token}
   ```
2. When the target clicks the link, the phishing server receives the request
3. The server extracts the `?t=` parameter, looks up the `campaign_target`
4. A `link_clicked` event is logged with IP, user agent, browser, OS, and device type
5. The target's status is updated to `clicked`
6. The landing page HTML is served to the target

**Note**: Static assets (`.css`, `.js`, `.png`, `.gif`, `.svg`, `.woff`, `.ttf`, etc.) are served without triggering tracking events — only HTML page requests are tracked.

### Form Submission Tracking

**Mechanism**: Landing page forms POST to a dedicated endpoint with the tracking token.

**Flow**:
1. The landing page form submits to `/api/submit?t={tracking_token}` (the token can also be passed as a hidden field named `_token` or `t`)
2. The phishing server receives the form data
3. The server detects whether credentials were submitted by checking for password-like field names (`password`, `passwd`, `pass`, `pwd`, `secret`)
4. An event is logged:
   - `credentials_captured` — if a password field was detected
   - `form_submitted` — for all other form data
5. A `FormSubmission` record is created with the captured field data
6. The target's status is updated to `submitted`
7. The target is redirected to the landing page's configured `redirect_url` (typically an awareness page)

### Target Status Progression

Each target's status progresses through a one-way lifecycle — it can only advance forward:

```
pending  →  sent  →  opened  →  clicked  →  submitted
```

| Status | Meaning |
|--------|---------|
| `pending` | Target assigned to campaign, email not yet sent |
| `sent` | Email successfully delivered via SMTP |
| `opened` | Tracking pixel loaded (email opened) |
| `clicked` | Phishing link clicked (landing page visited) |
| `submitted` | Form submitted on the landing page |

### Event Data

Every tracking event records:

| Field | Description |
|-------|-------------|
| `event_type` | `email_opened`, `link_clicked`, `form_submitted`, or `credentials_captured` |
| `ip_address` | Target's IP address (forwarded by Caddy) |
| `user_agent` | Full user agent string |
| `browser` | Detected browser (Chrome, Firefox, Safari, Edge, IE) |
| `os` | Detected OS (Windows, macOS, Linux, Android, iOS) |
| `device_type` | Detected device (desktop, mobile, tablet) |
| `created_at` | Timestamp of the event |

---

## Development

### Package Management

This project uses **UV** for Python package management and venv management:

```bash
# Install dependencies
uv pip install -r requirements.txt

# Install service-specific dependencies
uv pip install -r webadmin/requirements.txt
uv pip install -r worker/requirements.txt

# Sync dependencies from pyproject.toml
uv sync
```

### Running Services Locally

**WebAdmin (without Docker/Podman):**

```bash
cd webadmin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run application
export FLASK_DEBUG=True
export FLASK_PORT=8006
uv run python app.py
```

### Code Quality

Use the provided lint script for comprehensive code quality checks:

```bash
# Run all quality checks (Black + Flake8)
./lint.sh

# Auto-fix formatting issues
uv run black webadmin/ db/ redis/ worker/ alembic/

# Run individual tools
uv run black .                    # Format code
uv run flake8 .                   # Lint code
uv run mypy .                     # Type checking
uv run pylint webadmin/           # Advanced linting
uv run isort .                    # Sort imports
```

**Note**: All code quality tool configurations are in `pyproject.toml`.

### Database Migrations (Alembic)

The project uses Alembic for database schema migrations. SQLAlchemy models are defined in `db/models.py`.

```bash
# Create a new migration after changing models
uv run alembic revision --autogenerate -m "description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history

# View current revision
uv run alembic current
```

**Important**: Alembic requires `DATABASE_URL` environment variable to be set. Configuration is in `alembic/env.py` and `alembic.ini`.

---

## Security

### Authentication
- Session-based authentication with Redis backend
- Password hashing using werkzeug (PBKDF2-SHA256)
- HttpOnly, Secure, and SameSite cookie flags
- Flask-Login integration for user management

### Protection Mechanisms
- CSRF protection via Flask-WTF
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection via Jinja2 auto-escaping
- Input validation and sanitization
- Tracking token-based access control

### Best Practices
- Environment-based secrets management
- No hardcoded credentials in codebase
- Principle of least privilege for services
- Separate domains for admin and phishing pages
- Regular security audits and updates

### Container Security (Podman)
- Rootless container support
- Output redirection to prevent credential leaks
- User namespace isolation
- Enhanced cgroup controls

---

## Testing

Run the test suite:

```bash
# Run all tests (Docker)
docker-compose exec webadmin pytest tests/

# Run all tests (Podman)
podman exec phishly-webadmin pytest tests/

# Run specific test file
pytest tests/test_campaigns.py

# Run with coverage
pytest --cov=app tests/
```

---

## Troubleshooting

### Docker Issues

**Issue: Containers not starting**
```bash
# Check container status
docker-compose ps

# View logs
docker logs phishly-webadmin
docker logs celery-worker

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

**Issue: Port already in use**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8006

# Stop conflicting service or change FLASK_PORT in .env
```

### Podman Issues

**Issue: Credential exposure in terminal**
```bash
# Use the provided scripts (output is suppressed)
./podman_phishly-up.sh

# Or use aliases
pcup  # if aliases are configured
```

**Issue: Permission denied**
```bash
# Ensure scripts are executable
chmod +x podman_phishly-*.sh

# Check Podman socket
systemctl --user status podman.socket
systemctl --user start podman.socket
```

### Database Issues

**Issue: Database connection failed**
```bash
# Check database is running
docker exec postgres-db psql -U phishly_user -d phishly -c "SELECT 1;"

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

### Email Issues

**Issue: Emails not sending**
```bash
# Check SMTP configuration in .env
# View worker logs
docker logs -f celery-worker

# Test SMTP connection
docker exec celery-worker python -c "from tasks import test_smtp_connection; test_smtp_connection.delay()"
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
- Container support: [Docker](https://www.docker.com) & [Podman](https://podman.io)

### Sponsors

Special thanks to **Lycée Guillaume Kroll (LGK)** for their support and resources that made this project possible.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/phishly/phishly/issues)
- **Email:** phishly-team@example.com

---

<div align="center">

**[⬆ back to top](#-phishly)**

Made with ❤️ by the LuxGuard Team • © 2025 Phishly Project

</div>
