#!/bin/bash
# Phishly Shutdown Script (Podman version)
# Stops all services cleanly without deleting data

echo "🛑 Phishly Shutdown (Podman)..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}ℹ️  This will stop all services but preserve all data${NC}"
echo ""

# Check if containers are running
if ! podman-compose ps 2>/dev/null | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  No running containers found${NC}"
    echo ""
    echo "Containers are already stopped."
    echo ""
    exit 0
fi

# Stop all services gracefully (suppress output to avoid credential leaks)
echo "📋 Stopping all services..."
echo ""

# Stop application containers first (graceful shutdown)
echo "   → Stopping WebAdmin..."
podman-compose stop webadmin >/dev/null 2>&1

echo "   → Stopping Celery Worker..."
podman-compose stop celery-worker >/dev/null 2>&1

echo "   → Stopping Phishing Server..."
podman-compose stop phishing-server >/dev/null 2>&1

echo "   → Stopping Reverse Proxy..."
podman-compose stop caddy >/dev/null 2>&1

# Stop data services last
echo "   → Stopping Redis..."
podman-compose stop redis >/dev/null 2>&1

echo "   → Stopping PostgreSQL..."
podman-compose stop postgres >/dev/null 2>&1

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""

# Verify
echo "🔍 Verification..."
if podman-compose ps 2>/dev/null | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Some containers are still running:${NC}"
    podman-compose ps 2>/dev/null
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
echo "   • Podman images (ready for quick restart)"
echo ""
echo -e "${YELLOW}💡 To start services again:${NC}"
echo "   Quick restart:  ./podman_phishly-up.sh"
echo "   Full check:     ./podman_phishly-deploy.sh"
echo ""
echo -e "${RED}⚠️  To completely remove everything (including data):${NC}"
echo "   podman-compose down -v"
echo "   (Use with caution - this deletes all data!)"
echo ""
