#!/bin/bash
# Phishly Quick Restart Script (Podman version)
# Use this after reboot or to restart all services (preserves data)

set -e  # Exit on error

echo "🔄 Phishly Quick Restart (Podman)..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}ℹ️  This will start/restart all services while preserving all data${NC}"
echo ""

# Step 1: Check Podman
echo "📋 Step 1/3: Checking Podman..."
if ! command -v podman &> /dev/null; then
    echo "❌ Podman not found. Please install Podman first."
    exit 1
fi
if ! command -v podman-compose &> /dev/null; then
    echo "❌ Podman Compose not found. Please install Podman Compose first."
    exit 1
fi
echo -e "${GREEN}✅ Podman and Podman Compose found${NC}"
echo ""

# Step 2: Start all services (suppress output to avoid credential leaks)
echo "📋 Step 2/3: Starting all services..."
podman-compose up -d >/dev/null 2>&1
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
if podman exec redis-cache redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis: Connected${NC}"
else
    echo -e "${RED}❌ Redis: Connection failed${NC}"
fi

# Check PostgreSQL
if podman exec postgres-db psql -U phishly_user -d phishly -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL: Connected${NC}"
else
    echo -e "${RED}❌ PostgreSQL: Connection failed${NC}"
fi

# Check Celery Worker
if podman ps 2>/dev/null | grep celery-worker | grep -q Up; then
    echo -e "${GREEN}✅ Celery Worker: Running${NC}"
else
    echo -e "${RED}❌ Celery Worker: Not running${NC}"
fi

# Check Phishing Server
if podman ps 2>/dev/null | grep phishly-phishing | grep -q Up; then
    echo -e "${GREEN}✅ Phishing Server: Running${NC}"
else
    echo -e "${RED}❌ Phishing Server: Not running${NC}"
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
echo "   Check status:  podman-compose ps"
echo "   View logs:     podman logs -f phishly-webadmin"
echo "   Stop all:      ./podman_phishly-down.sh"
echo "   Full redeploy: ./podman_phishly-deploy.sh"
echo ""
echo "💡 Tip: Use aliases to avoid credential leaks:"
echo "   alias pcup='podman-compose up -d >/dev/null 2>&1'"
echo "   alias pcdown='podman-compose down >/dev/null 2>&1'"
echo ""
echo "Happy Testing! 🚀"
echo ""
