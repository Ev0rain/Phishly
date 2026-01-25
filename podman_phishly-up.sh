#!/bin/bash
# Phishly Quick Start Script (Podman version)
# Use this after reboot or to start all services (preserves data)

set -e  # Exit on error

echo "Phishly Quick Start (Podman)..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get current user's UID and GID (works on any machine)
CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)

# Export for compose to use
export PUID=$CURRENT_UID
export PGID=$CURRENT_GID

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

# Function to fix Podman volume permissions
fix_volume_permissions() {
    echo "Fixing Podman volume permissions for UID:GID $CURRENT_UID:$CURRENT_GID..."

    # List of volumes that need write access
    VOLUMES=(
        "phishly_dns_zone_files"
        "phishly_landing_page_cache"
        "phishly_campaign_deployments"
    )

    for vol in "${VOLUMES[@]}"; do
        # Check if volume exists
        if podman volume inspect "$vol" > /dev/null 2>&1; then
            echo "   -> Fixing $vol"
            podman run --rm -v "$vol":/data alpine chown -R "$CURRENT_UID:$CURRENT_GID" /data 2>/dev/null || true
        fi
    done

    echo -e "${GREEN}Volume permissions fixed${NC}"
}

echo -e "${GREEN}This will start all services while preserving all data${NC}"
echo ""

# Step 1: Check Podman
echo "Step 1/4: Checking Podman..."
if ! command -v podman &> /dev/null; then
    echo -e "${RED}Podman not found. Please install Podman first.${NC}"
    exit 1
fi
echo -e "${GREEN}Podman found (using: $COMPOSE_CMD)${NC}"
echo ""

# Step 2: Start all services (creates volumes if missing)
echo "Step 2/4: Starting all services..."
$COMPOSE_CMD up -d
echo -e "${GREEN}Services started${NC}"
echo ""

# Step 3: Fix volume permissions (after volumes are created/mounted)
echo "Step 3/4: Fixing volume permissions..."
fix_volume_permissions
echo ""

# Step 4: Wait and verify
echo "Step 4/4: Waiting for services to be ready (15 seconds)..."
sleep 15
echo -e "${GREEN}Services should be ready${NC}"
echo ""

# Health checks
echo "Running health checks..."

# Check webadmin
if curl -f -s http://localhost:8006/health > /dev/null 2>&1; then
    echo -e "${GREEN}WebAdmin: Healthy${NC}"
else
    echo -e "${YELLOW}WebAdmin: Not ready yet (may need more time)${NC}"
fi

# Check Redis
if podman exec redis-cache redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}Redis: Connected${NC}"
else
    echo -e "${RED}Redis: Connection failed${NC}"
fi

# Check PostgreSQL
if podman exec postgres-db pg_isready -U "${POSTGRES_USER:-phishly_user}" > /dev/null 2>&1; then
    echo -e "${GREEN}PostgreSQL: Connected${NC}"
else
    echo -e "${RED}PostgreSQL: Connection failed${NC}"
fi

# Check Celery Worker
if podman ps 2>/dev/null | grep celery-worker | grep -qE "(Up|running)"; then
    echo -e "${GREEN}Celery Worker: Running${NC}"
else
    echo -e "${RED}Celery Worker: Not running${NC}"
fi

# Check Phishing Server
if podman ps 2>/dev/null | grep phishly-phishing | grep -qE "(Up|running)"; then
    echo -e "${GREEN}Phishing Server: Running${NC}"
else
    echo -e "${RED}Phishing Server: Not running${NC}"
fi

echo ""

# Summary
echo "============================================"
echo "   START COMPLETE!"
echo "============================================"
echo ""
echo -e "${GREEN}What was preserved:${NC}"
echo "   - All database data"
echo "   - Redis cache and queued tasks"
echo "   - Email jobs and campaign history"
echo "   - User accounts and settings"
echo ""
echo "Access Point:"
echo "   https://phishly.btslgk.lu:8006"
echo "   (Add 'phishly.btslgk.lu' to /etc/hosts pointing to your server IP)"
echo ""
echo "Useful Commands:"
echo "   Check status:  $COMPOSE_CMD ps"
echo "   View logs:     podman logs -f phishly-webadmin"
echo "   Stop all:      ./podman_phishly-down.sh"
echo "   Full redeploy: ./podman_phishly-deploy.sh"
echo ""
