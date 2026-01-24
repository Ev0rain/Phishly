#!/bin/bash
# Phishly Quick Restart Script (Podman version)
# Restarts all containers without stopping them (preserves data)

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔄 Restarting Phishly services (Podman)..."
echo ""

# Restart all services (suppress output to avoid credential leaks)
podman-compose restart >/dev/null 2>&1

echo ""
echo -e "${GREEN}✅ All services restarted${NC}"
echo ""

# Quick health check
echo "📋 Service Status:"
podman-compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || podman-compose ps 2>/dev/null

echo ""
echo "💡 Tip: Use aliases to avoid credential leaks:"
echo "   alias pcup='podman-compose up -d >/dev/null 2>&1'"
echo "   alias pcdown='podman-compose down >/dev/null 2>&1'"
echo ""
