#!/usr/bin/env python3
"""
Phishly Pre-Deployment Validation Script

Checks that all components are ready for deployment.
Run this before starting Docker containers.
"""

import os
import sys
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")

def check_pass(message):
    print(f"{GREEN}✅ {message}{RESET}")
    return True

def check_fail(message):
    print(f"{RED}❌ {message}{RESET}")
    return False

def check_warn(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Environment Configuration Check")

    env_path = Path(".env")
    if not env_path.exists():
        check_fail(".env file not found!")
        print(f"   Create it from .env.template: cp .env.template .env")
        return False

    check_pass(".env file exists")

    # Parse .env file
    env_vars = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    # Check required variables
    required_vars = [
        ("POSTGRES_DB", "phishly"),
        ("POSTGRES_USER", None),
        ("POSTGRES_PASSWORD", None),
        ("SECRET_KEY", None),
        ("SMTP_HOST", None),
        ("SMTP_PORT", "587"),
        ("SMTP_USER", None),
        ("SMTP_PASSWORD", None),
        ("PHISHING_DOMAIN", None),
    ]

    all_good = True
    for var_name, expected in required_vars:
        value = env_vars.get(var_name, "")

        if not value or "CHANGE_THIS" in value:
            check_fail(f"{var_name} is not set or using placeholder")
            all_good = False
        elif expected and value != expected:
            check_warn(f"{var_name} = {value} (expected: {expected})")
        else:
            # Mask sensitive values
            if "PASSWORD" in var_name or "SECRET" in var_name:
                display = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display = value
            check_pass(f"{var_name} = {display}")

    return all_good

def check_docker_files():
    """Check if Docker files exist and are valid"""
    print_header("Docker Configuration Check")

    all_good = True

    # Check docker-compose.yml
    if not Path("docker-compose.yml").exists():
        check_fail("docker-compose.yml not found")
        all_good = False
    else:
        check_pass("docker-compose.yml exists")

    # Check Dockerfiles
    dockerfiles = [
        "webadmin/Dockerfile",
        "worker/Dockerfile"
    ]

    for dockerfile in dockerfiles:
        if not Path(dockerfile).exists():
            check_fail(f"{dockerfile} not found")
            all_good = False
        else:
            check_pass(f"{dockerfile} exists")

    return all_good

def check_required_directories():
    """Check if required directories exist"""
    print_header("Project Structure Check")

    all_good = True

    required_dirs = [
        "webadmin",
        "webadmin/routes",
        "webadmin/repositories",
        "webadmin/templates",
        "webadmin/static",
        "webadmin/scripts",
        "webadmin/migrations",
        "worker",
        "db",
        "redis",
        "templates/email_templates"
    ]

    for dir_path in required_dirs:
        if not Path(dir_path).is_dir():
            check_fail(f"Directory missing: {dir_path}")
            all_good = False
        else:
            check_pass(f"Directory exists: {dir_path}")

    return all_good

def check_database_files():
    """Check if database models and migrations exist"""
    print_header("Database Configuration Check")

    all_good = True

    # Check models
    if not Path("db/models.py").exists():
        check_fail("db/models.py not found")
        all_good = False
    else:
        check_pass("Database models exist (db/models.py)")

    # Check webadmin database integration
    if not Path("webadmin/database.py").exists():
        check_fail("webadmin/database.py not found")
        all_good = False
    else:
        check_pass("WebAdmin database module exists")

    # Check auth utils
    if not Path("webadmin/auth_utils.py").exists():
        check_fail("webadmin/auth_utils.py not found")
        all_good = False
    else:
        check_pass("Authentication utilities exist")

    # Check migrations
    migrations_dir = Path("alembic/versions")
    if migrations_dir.exists():
        migrations = list(migrations_dir.glob("*.py"))
        if migrations:
            check_pass(f"Database migrations exist ({len(migrations)} migration(s))")
        else:
            check_warn("No database migrations found in alembic/versions/")
    else:
        check_warn("Alembic migrations directory not found")

    # Check initialization scripts
    if Path("webadmin/scripts/create_admin.py").exists():
        check_pass("Admin creation script exists")
    else:
        check_warn("Admin creation script not found")

    if Path("webadmin/scripts/seed_database.py").exists():
        check_pass("Database seeding script exists")
    else:
        check_warn("Database seeding script not found")

    return all_good

def check_worker_files():
    """Check if worker files exist"""
    print_header("Celery Worker Check")

    all_good = True

    worker_files = [
        "worker/tasks.py",
        "worker/email_sender.py",
        "worker/email_renderer.py",
        "worker/database.py",
        "worker/requirements.txt"
    ]

    for file_path in worker_files:
        if not Path(file_path).exists():
            check_fail(f"{file_path} not found")
            all_good = False
        else:
            check_pass(f"{file_path} exists")

    return all_good

def check_email_templates():
    """Check if email templates exist"""
    print_header("Email templates Check")

    templates_dir = Path("templates/email_templates")
    if not templates_dir.exists():
        check_fail("templates/email_templates directory not found")
        return False

    templates = list(templates_dir.glob("*.html")) + list(templates_dir.glob("*.txt"))

    if len(templates) == 0:
        check_fail("No email templates found")
        return False
    else:
        check_pass(f"Found {len(templates)} email template(s)")
        return True

def check_requirements():
    """Check if requirements files exist"""
    print_header("Dependencies Check")

    all_good = True

    req_files = [
        "webadmin/requirements.txt",
        "worker/requirements.txt",
        "requirements.txt"
    ]

    for req_file in req_files:
        if not Path(req_file).exists():
            check_warn(f"{req_file} not found")
        else:
            check_pass(f"{req_file} exists")

    return all_good

def main():
    print(f"{BOLD}{BLUE}")
    print(r"""
    ____  __    _      __    __     
   / __ \/ /_  (_)____/ /_  / /_  __
  / /_/ / __ \/ / ___/ __ \/ / / / /
 / ____/ / / / (__  ) / / / / /_/ / 
/_/   /_/ /_/_/____/_/ /_/_/\__, /  
                           /____/   
Pre-Deployment Validation
    """)
    print(RESET)

    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Run all checks
    results = []

    results.append(("Environment", check_env_file()))
    results.append(("Docker", check_docker_files()))
    results.append(("Structure", check_required_directories()))
    results.append(("Database", check_database_files()))
    results.append(("Worker", check_worker_files()))
    results.append(("templates", check_email_templates()))
    results.append(("Dependencies", check_requirements()))

    # Summary
    print_header("Validation Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{name:20} [{status}]")

    print(f"\n{BOLD}Result: {passed}/{total} checks passed{RESET}\n")

    if passed == total:
        print(f"{GREEN}{BOLD}✅ All checks passed! Ready for deployment.{RESET}")
        print(f"\n{BLUE}Next steps:{RESET}")
        print(f"  1. Start services: {BOLD}docker-compose up -d{RESET}")
        print(f"  2. Create admin user: {BOLD}docker-compose exec webadmin python scripts/create_admin.py{RESET}")
        print(f"  3. Seed database: {BOLD}docker-compose exec webadmin python scripts/seed_database.py{RESET}")
        print(f"  4. Access dashboard: {BOLD}http://localhost:8006{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}❌ Some checks failed. Please fix the issues above.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

