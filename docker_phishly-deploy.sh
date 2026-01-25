#!/bin/bash
# Phishly Quick Deploy Script
# This script deploys the entire Phishly platform

set -e  # Exit on error

echo "Phishly Quick Deploy Starting..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get current user's UID and GID (works on any machine)
CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)

# Export for docker-compose to use
export PUID=$CURRENT_UID
export PGID=$CURRENT_GID

# Function to fix Docker volume permissions
fix_volume_permissions() {
    echo "Fixing Docker volume permissions for UID:GID $CURRENT_UID:$CURRENT_GID..."

    # List of volumes that need write access
    VOLUMES=(
        "phishly_dns_zone_files"
        "phishly_landing_page_cache"
        "phishly_campaign_deployments"
    )

    for vol in "${VOLUMES[@]}"; do
        # Check if volume exists
        if docker volume inspect "$vol" > /dev/null 2>&1; then
            echo "   -> Fixing $vol"
            docker run --rm -v "$vol":/data alpine chown -R "$CURRENT_UID:$CURRENT_GID" /data 2>/dev/null || true
        fi
    done

    echo -e "${GREEN}Volume permissions fixed${NC}"
}

# Step 1: Check Docker
echo "Step 1/6: Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please install Docker first.${NC}"
    exit 1
fi
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker and Docker Compose found${NC}"
echo ""

# Step 2: Initialize local directories
echo "Step 2/6: Initializing local directory structure..."
if [ -f "./init_directories.sh" ]; then
    chmod +x ./init_directories.sh
    ./init_directories.sh
else
    echo -e "${YELLOW}init_directories.sh not found, skipping local directory initialization${NC}"
fi
echo ""

# Step 3: Start Services (this creates volumes if they don't exist)
echo "Step 3/6: Starting all services..."
docker compose up -d
echo -e "${GREEN}Services started${NC}"
echo ""

# Step 4: Fix volume permissions (after volumes are created)
echo "Step 4/6: Fixing volume permissions..."
fix_volume_permissions
echo ""

# Step 5: Wait for services to initialize
echo "Step 5/6: Waiting for services to initialize (30 seconds)..."
sleep 30
echo -e "${GREEN}Services initialized${NC}"
echo ""

# Step 6: Initialize database (create tables + admin user)
echo "Step 6/6: Initializing database..."
docker exec phishly-webadmin python -c "
import sys
import os
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash
from datetime import datetime

# Import models
sys.path.insert(0, '/app')
os.chdir('/app')
from db.models import Base, AdminUser

# Get database URL from environment
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('DATABASE_URL not set')
    sys.exit(1)

# Create engine and tables
engine = create_engine(db_url)
Base.metadata.create_all(engine)
print('Database tables created')

# Create session and add admin user
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Check if admin exists
    existing = session.query(AdminUser).filter_by(username='admin').first()
    if not existing:
        admin = AdminUser(
            username='admin',
            email='admin@phishly.local',
            password_hash=generate_password_hash('admin123'),
            full_name='System Administrator',
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(admin)
        session.commit()
        print('Admin user created: admin / admin123')
    else:
        print('Admin user already exists')
except Exception as e:
    print(f'Error creating admin: {e}')
    session.rollback()
finally:
    session.close()
" 2>&1 | grep -E "^(Database|Admin|Error)" || true
echo -e "${GREEN}Database initialized${NC}"
echo ""

# Verification
echo "Verifying deployment..."
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}Containers are running${NC}"
else
    echo -e "${YELLOW}Some containers may not be running. Check with: docker compose ps${NC}"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8006/health 2>/dev/null | grep -q "200"; then
    echo -e "${GREEN}WebAdmin is responding${NC}"
else
    echo -e "${YELLOW}WebAdmin may not be ready yet. Wait a moment and check: curl http://localhost:8006/health${NC}"
fi

# Check phishing server
if docker ps | grep phishly-phishing | grep -q Up; then
    echo -e "${GREEN}Phishing Server is running${NC}"
else
    echo -e "${YELLOW}Phishing Server may not be running. Check with: docker compose ps${NC}"
fi

# Success message
echo ""
echo "============================================"
echo "   DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo -e "${GREEN}Access Point:${NC}"
echo "   https://phishly.btslgk.lu:8006"
echo "   (Add 'phishly.btslgk.lu' to /etc/hosts pointing to your server IP)"
echo ""
echo -e "${GREEN}Login Credentials:${NC}"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo -e "${YELLOW}Remember to change the password after first login!${NC}"
echo ""
echo "Useful Commands:"
echo "   Check status:  docker compose ps"
echo "   View logs:     docker logs -f phishly-webadmin"
echo "   Stop all:      ./docker_phishly-down.sh"
echo "   Restart:       ./docker_phishly-restart.sh"
echo ""
