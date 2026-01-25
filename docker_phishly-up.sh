#!/bin/bash
# Phishly Quick Start Script
# Use this after reboot or to start all services (preserves data)

set -e  # Exit on error

echo "Phishly Quick Start..."
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

echo -e "${GREEN}This will start all services while preserving all data${NC}"
echo ""

# Step 1: Check Docker
echo "Step 1/4: Checking Docker..."
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

# Step 2: Start all services (creates volumes if missing)
echo "Step 2/4: Starting all services..."
docker compose up -d
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
if docker exec redis-cache redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}Redis: Connected${NC}"
else
    echo -e "${RED}Redis: Connection failed${NC}"
fi

# Check PostgreSQL
if docker exec postgres-db pg_isready -U "${POSTGRES_USER:-phishly_user}" > /dev/null 2>&1; then
    echo -e "${GREEN}PostgreSQL: Connected${NC}"
else
    echo -e "${RED}PostgreSQL: Connection failed${NC}"
fi

# Check Celery Worker
if docker ps | grep celery-worker | grep -q Up; then
    echo -e "${GREEN}Celery Worker: Running${NC}"
else
    echo -e "${RED}Celery Worker: Not running${NC}"
fi

# Check Phishing Server
if docker ps | grep phishly-phishing | grep -q Up; then
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
echo "   Check status:  docker compose ps"
echo "   View logs:     docker logs -f phishly-webadmin"
echo "   Stop all:      ./docker_phishly-down.sh"
echo "   Full redeploy: ./docker_phishly-deploy.sh"
echo ""
