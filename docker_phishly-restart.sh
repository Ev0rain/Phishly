#!/bin/bash
# Phishly Quick Restart Script
# Restarts all containers (preserves data)

set -e  # Exit on error

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
            docker run --rm -v "$vol":/data alpine chown -R "$CURRENT_UID:$CURRENT_GID" /data 2>/dev/null || true
        fi
    done

    echo -e "${GREEN}Volume permissions fixed${NC}"
}

echo "Restarting Phishly services..."
echo ""

# Fix volume permissions before restart
echo "Step 1/2: Fixing volume permissions..."
fix_volume_permissions
echo ""

# Restart all services
echo "Step 2/2: Restarting containers..."
docker compose restart

echo ""
echo -e "${GREEN}All services restarted${NC}"
echo ""

# Quick health check
echo "Service Status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}"
echo ""

# Wait a moment and check health
sleep 5
if curl -f -s http://localhost:8006/health > /dev/null 2>&1; then
    echo -e "${GREEN}WebAdmin: Healthy${NC}"
else
    echo -e "${YELLOW}WebAdmin: Starting up (check in a few seconds)${NC}"
fi
echo ""
