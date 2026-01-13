#!/bin/bash
# Phishly Quick Restart Script
# Use this after reboot or to restart all services (preserves data)

set -e  # Exit on error

echo "🔄 Phishly Quick Restart..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}ℹ️  This will start/restart all services while preserving all data${NC}"
echo ""

# Step 1: Check Docker
echo "📋 Step 1/3: Checking Docker..."
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

# Step 2: Start all services (creates if missing, restarts if running)
echo "📋 Step 2/3: Starting all services..."
docker-compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 3: Wait and verify
echo "📋 Step 3/3: Waiting for services to be ready (15 seconds)..."
sleep 15
echo -e "${GREEN}✅ Services should be ready${NC}"
echo ""

# Health checks
echo "🔍 Running health checks..."

# Check webadmin
if curl -f -s http://localhost:8006/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ WebAdmin: Healthy${NC}"
else
    echo -e "${YELLOW}⚠️  WebAdmin: Not ready yet (may need more time)${NC}"
fi

# Check Redis
if docker exec redis-cache redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis: Connected${NC}"
else
    echo -e "${RED}❌ Redis: Connection failed${NC}"
fi

# Check PostgreSQL
if docker exec postgres-db psql -U phishly_user -d phishly -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL: Connected${NC}"
else
    echo -e "${RED}❌ PostgreSQL: Connection failed${NC}"
fi

# Check Celery Worker
if docker ps | grep celery-worker | grep -q Up; then
    echo -e "${GREEN}✅ Celery Worker: Running${NC}"
else
    echo -e "${RED}❌ Celery Worker: Not running${NC}"
fi

echo ""

# Summary
echo "🎉 ============================================"
echo "   RESTART COMPLETE!"
echo "============================================"
echo ""
echo -e "${GREEN}✅ What was preserved:${NC}"
echo "   • All database data"
echo "   • Redis cache and queued tasks"
echo "   • Email jobs and campaign history"
echo "   • User accounts and settings"
echo ""
echo "🌐 Access Point:"
echo "   http://localhost:8006"
echo ""
echo "📊 Useful Commands:"
echo "   Check status:  docker-compose ps"
echo "   View logs:     docker logs -f phishly-webadmin"
echo "   Stop all:      ./down.sh"
echo "   Full redeploy: ./deploy.sh"
echo ""
echo "Happy Testing! 🚀"
echo ""

