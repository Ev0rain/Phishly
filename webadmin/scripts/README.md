# Webadmin Scripts
- Or manually insert event types into database
- Run seed_database.py first (creates event types)
**"Event type not found"**:

- Check existing AdminUser records
- Use a different username or email
**"Username already exists"**:

- Verify credentials
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
**"Database connection failed"**:

## Troubleshooting

   - Use credentials created in step 3
   - Navigate to http://localhost:8006/login
6. **Login**:

   ```
   uv run python app.py
   ```bash
5. **Start application**:

   ```
   uv run python scripts/seed_database.py
   ```bash
4. **Seed development data** (optional):

   ```
   uv run python scripts/create_admin.py
   ```bash
3. **Create admin user**:

   ```
   uv run alembic upgrade head
   ```bash
2. **Run migrations**:

   ```
   # Edit .env with database credentials
   cp .env.example .env
   ```bash
1. **Configure environment**:

## Setup Workflow

- All dependencies installed (`uv pip install -r requirements.txt`)
- Flask application context
- Database connection configured in `.env`
Both scripts require:

## Requirements

- Generates realistic activity patterns for testing analytics
- Event types must be seeded first (required by other tables)
- Safe to run multiple times (checks for existing data)
**Notes**:

  - Timestamps spread over last 60 days
  - Events generated with realistic patterns (60% open rate, 40% click rate, etc.)
  - Each campaign has multiple targets
- **Campaigns**: 5 sample campaigns with realistic event data
- **Target Lists**: 5 target lists (department-based, ~10 members each)
- **Email Templates**: 5 email templates with metadata
- **Targets**: 30 sample targets with realistic names across departments
- **Departments**: 8 departments (Engineering, Finance, Sales, etc.)
- **Event Types**: email_sent, email_opened, link_clicked, form_submitted, credentials_captured
**Creates**:

```
uv run python scripts/seed_database.py
cd webadmin
```bash
**Usage**:

Populates the database with sample development data for testing.

### seed_database.py

- Password confirmation match
- Email uniqueness
- Username uniqueness
**Checks**:

- Full name (optional)
- Password (with confirmation)
- Email
- Username
**Prompts for**:

```
uv run python scripts/create_admin.py
cd webadmin
```bash
**Usage**:

Interactive script to create admin users for webadmin authentication.

### create_admin.py

## Scripts

This directory contains utility scripts for Phishly webadmin setup and management.


