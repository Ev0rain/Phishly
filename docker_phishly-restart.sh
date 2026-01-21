#!/bin/bash
# Phishly Quick Restart Script
# Restarts all containers without stopping them (preserves data)

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔄 Restarting Phishly services..."
echo ""

# Restart all services
docker-compose restart

echo ""
echo -e "${GREEN}✅ All services restarted${NC}"
echo ""

# Quick health check
echo "📋 Service Status:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}"
