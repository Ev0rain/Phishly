#!/bin/bash
# Phishly Shutdown Script (Podman version)
# Stops all services cleanly without deleting data

echo "Phishly Shutdown (Podman)..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect compose command (podman-compose or podman compose)
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif podman compose version &> /dev/null; then
    COMPOSE_CMD="podman compose"
else
    echo -e "${RED}Neither podman-compose nor 'podman compose' found.${NC}"
    echo "Install with: pip install podman-compose"
    exit 1
fi

echo -e "${YELLOW}This will stop all services but preserve all data${NC}"
echo ""

# Check if containers are running
if ! $COMPOSE_CMD ps 2>/dev/null | grep -qE "(Up|running)"; then
    echo -e "${YELLOW}No running containers found${NC}"
    echo ""
    echo "Containers are already stopped."
    echo ""
    exit 0
fi

# Stop all services gracefully
echo "Stopping all services..."
echo ""

# Stop application containers first (graceful shutdown)
echo "   -> Stopping WebAdmin..."
$COMPOSE_CMD stop webadmin 2>/dev/null || true

echo "   -> Stopping Celery Worker..."
$COMPOSE_CMD stop celery-worker 2>/dev/null || true

echo "   -> Stopping Phishing Server..."
$COMPOSE_CMD stop phishing-server 2>/dev/null || true

echo "   -> Stopping Reverse Proxy..."
$COMPOSE_CMD stop caddy 2>/dev/null || true

# Stop data services last
echo "   -> Stopping Redis..."
$COMPOSE_CMD stop redis 2>/dev/null || true

echo "   -> Stopping PostgreSQL..."
$COMPOSE_CMD stop postgres 2>/dev/null || true

echo ""
echo -e "${GREEN}All services stopped${NC}"
echo ""

# Verify
echo "Verification..."
if $COMPOSE_CMD ps 2>/dev/null | grep -qE "(Up|running)"; then
    echo -e "${YELLOW}Some containers are still running:${NC}"
    $COMPOSE_CMD ps 2>/dev/null
else
    echo -e "${GREEN}All containers stopped successfully${NC}"
fi

echo ""

# Summary
echo "============================================"
echo "   SHUTDOWN COMPLETE!"
echo "============================================"
echo ""
echo -e "${GREEN}What was preserved:${NC}"
echo "   - All database data (PostgreSQL volumes)"
echo "   - Redis data and configuration"
echo "   - Email jobs and campaign history"
echo "   - User accounts and settings"
echo "   - Podman images (ready for quick restart)"
echo ""
echo -e "${YELLOW}To start services again:${NC}"
echo "   Quick start:   ./podman_phishly-up.sh"
echo "   Full deploy:   ./podman_phishly-deploy.sh"
echo ""
echo -e "${RED}To completely remove everything (including data):${NC}"
echo "   $COMPOSE_CMD down -v"
echo "   (Use with caution - this deletes all data!)"
echo ""
