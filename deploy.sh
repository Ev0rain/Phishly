#!/bin/bash
# Phishly Quick Deploy Script
# This script deploys the entire Phishly platform in under 2 minutes

set -e  # Exit on error

echo "🚀 Phishly Quick Deploy Starting..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Docker
echo "📋 Step 1/5: Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi
echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"
echo ""

# Step 2: Start Services
echo "📋 Step 2/5: Starting all services..."
docker-compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 3: Wait for services to initialize
echo "📋 Step 3/5: Waiting for services to initialize (30 seconds)..."
sleep 30
echo -e "${GREEN}✅ Services initialized${NC}"
echo ""

# Step 4: Initialize database (create tables + admin user)
echo "📋 Step 4/5: Initializing database..."
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
    print('⚠️  DATABASE_URL not set')
    sys.exit(1)

# Create engine and tables
engine = create_engine(db_url)
Base.metadata.create_all(engine)
print('✅ Database tables created')

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
        print('✅ Admin user created: admin / admin123')
    else:
        print('ℹ️  Admin user already exists')
except Exception as e:
    print(f'⚠️  Error creating admin: {e}')
    session.rollback()
finally:
    session.close()
" 2>&1 | grep -E "^(✅|ℹ️|⚠️)"
echo -e "${GREEN}✅ Database initialized${NC}"
echo ""

# Step 5: Restart webadmin to clear any session issues
echo "📋 Step 5/5: Restarting webadmin (clears Redis sessions)..."
docker-compose restart webadmin > /dev/null 2>&1
sleep 5
echo -e "${GREEN}✅ WebAdmin restarted with clean sessions${NC}"
echo ""

# Verification
echo "🔍 Verifying deployment..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers are running${NC}"
else
    echo -e "${YELLOW}⚠️  Some containers may not be running. Check with: docker-compose ps${NC}"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8006/health | grep -q "200"; then
    echo -e "${GREEN}✅ WebAdmin is responding${NC}"
else
    echo -e "${YELLOW}⚠️  WebAdmin may not be ready yet. Wait a moment and check: curl http://localhost:8006/health${NC}"
fi

# Success message
echo ""
echo "🎉 ============================================"
echo "   DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo -e "${GREEN}📍 Access Point:${NC}"
echo "   🌐 http://localhost:8006"
echo ""
echo -e "${GREEN}🔐 Login Credentials:${NC}"
echo "   👤 Username: admin"
echo "   🔑 Password: admin123"
echo ""
echo -e "${YELLOW}⚠️  Remember to change the password after first login!${NC}"
echo ""
echo "📊 Useful Commands:"
echo "   Check status:  docker-compose ps"
echo "   View logs:     docker logs -f phishly-webadmin"
echo "   Stop all:      docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "Happy Testing! 🚀"

