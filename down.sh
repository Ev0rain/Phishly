#!/bin/bash
# Phishly Shutdown Script
# Stops all services cleanly without deleting data

echo "🛑 Phishly Shutdown..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}ℹ️  This will stop all services but preserve all data${NC}"
echo ""

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  No running containers found${NC}"
    echo ""
    echo "Containers are already stopped."
    echo ""
    exit 0
fi

# Stop all services gracefully
echo "📋 Stopping all services..."
echo ""

# Stop application containers first (graceful shutdown)
echo "   → Stopping WebAdmin..."
docker-compose stop webadmin

echo "   → Stopping Celery Worker..."
docker-compose stop celery-worker

echo "   → Stopping Reverse Proxy..."
docker-compose stop caddy

# Stop data services last
echo "   → Stopping Redis..."
docker-compose stop redis

echo "   → Stopping PostgreSQL..."
docker-compose stop postgres

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""

# Verify
echo "🔍 Verification..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Some containers are still running:${NC}"
    docker-compose ps
else
    echo -e "${GREEN}✅ All containers stopped successfully${NC}"
fi

echo ""

# Summary
echo "✅ ============================================"
echo "   SHUTDOWN COMPLETE!"
echo "============================================"
echo ""
echo -e "${GREEN}📦 What was preserved:${NC}"
echo "   • All database data (PostgreSQL volumes)"
echo "   • Redis data and configuration"
echo "   • Email jobs and campaign history"
echo "   • User accounts and settings"
echo "   • Docker images (ready for quick restart)"
echo ""
echo -e "${YELLOW}💡 To start services again:${NC}"
echo "   Quick restart:  ./re-deploy-production.sh"
echo "   Full check:     ./deploy.sh"
echo ""
echo -e "${RED}⚠️  To completely remove everything (including data):${NC}"
echo "   docker-compose down -v"
echo "   (Use with caution - this deletes all data!)"
echo ""
