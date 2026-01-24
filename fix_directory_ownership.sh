#!/bin/bash
# One-time fix for root-owned directories
# Run this script with: sudo ./fix_directory_ownership.sh

set -e

echo "🔧 Fixing directory ownership..."
echo ""

# Get the user who invoked sudo (or current user if run directly)
if [ -n "$SUDO_USER" ]; then
    TARGET_USER="$SUDO_USER"
    USER_ID=$(id -u "$SUDO_USER")
    GROUP_ID=$(id -g "$SUDO_USER")
else
    TARGET_USER="$USER"
    USER_ID=$(id -u)
    GROUP_ID=$(id -g)
fi

echo "Setting ownership to: $TARGET_USER ($USER_ID:$GROUP_ID)"
echo ""

# Fix webadmin/email_templates_imported if it's root-owned
if [ -d "webadmin/email_templates_imported" ]; then
    CURRENT_OWNER=$(stat -c '%u:%g' webadmin/email_templates_imported)
    if [ "$CURRENT_OWNER" != "$USER_ID:$GROUP_ID" ]; then
        echo "Fixing: webadmin/email_templates_imported (currently $CURRENT_OWNER)"
        chown -R "$USER_ID:$GROUP_ID" webadmin/email_templates_imported
        echo "✅ Fixed"
    else
        echo "✓ webadmin/email_templates_imported already has correct ownership"
    fi
else
    echo "✓ Creating: webadmin/email_templates_imported"
    mkdir -p webadmin/email_templates_imported
    chown "$USER_ID:$GROUP_ID" webadmin/email_templates_imported
fi

# Fix webadmin/dns_zones if needed
if [ -d "webadmin/dns_zones" ]; then
    CURRENT_OWNER=$(stat -c '%u:%g' webadmin/dns_zones)
    if [ "$CURRENT_OWNER" != "$USER_ID:$GROUP_ID" ]; then
        echo "Fixing: webadmin/dns_zones (currently $CURRENT_OWNER)"
        chown -R "$USER_ID:$GROUP_ID" webadmin/dns_zones
        echo "✅ Fixed"
    else
        echo "✓ webadmin/dns_zones already has correct ownership"
    fi
else
    echo "✓ Creating: webadmin/dns_zones"
    mkdir -p webadmin/dns_zones
    chown "$USER_ID:$GROUP_ID" webadmin/dns_zones
fi

# Create .gitkeep files if they don't exist
echo ""
echo "Creating .gitkeep files..."

if [ ! -f "webadmin/email_templates_imported/.gitkeep" ]; then
    touch webadmin/email_templates_imported/.gitkeep
    chown "$USER_ID:$GROUP_ID" webadmin/email_templates_imported/.gitkeep
    echo "✅ Created webadmin/email_templates_imported/.gitkeep"
else
    echo "✓ webadmin/email_templates_imported/.gitkeep exists"
fi

if [ ! -f "webadmin/dns_zones/.gitkeep" ]; then
    touch webadmin/dns_zones/.gitkeep
    chown "$USER_ID:$GROUP_ID" webadmin/dns_zones/.gitkeep
    echo "✅ Created webadmin/dns_zones/.gitkeep"
else
    echo "✓ webadmin/dns_zones/.gitkeep exists"
fi

echo ""
echo "✅ All done! Directory ownership fixed."
echo ""
echo "You can now run deployment scripts normally:"
echo "  ./docker_phishly-deploy.sh  (Docker)"
echo "  ./podman_phishly-deploy.sh  (Podman)"
echo ""
