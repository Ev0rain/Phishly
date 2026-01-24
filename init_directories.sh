#!/bin/bash
# Initialize directory structure with correct permissions
# Run this before first deployment to prevent root ownership issues

set -e

echo "🔧 Initializing Phishly directory structure..."
echo ""

# Get current user and group
USER_ID=$(id -u)
GROUP_ID=$(id -g)

echo "Creating directories as user $USER_ID:$GROUP_ID"
echo ""

# Create directories that containers will write to
DIRECTORIES=(
    "webadmin/email_templates_imported"
    "webadmin/dns_zones"
    "templates/email_templates"
    "templates/landing_pages"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ Directory exists: $dir"

        # Check ownership
        OWNER=$(stat -c '%u:%g' "$dir" 2>/dev/null || stat -f '%u:%g' "$dir" 2>/dev/null)
        if [ "$OWNER" != "$USER_ID:$GROUP_ID" ]; then
            echo "  ⚠️  Fixing ownership: $OWNER → $USER_ID:$GROUP_ID"

            # Try without sudo first
            if chown -R "$USER_ID:$GROUP_ID" "$dir" 2>/dev/null; then
                echo "  ✓ Ownership fixed"
            else
                echo "  ⚠️  Need sudo to fix ownership"
                echo "  Run: sudo ./fix_directory_ownership.sh"
                echo "  (One-time setup to fix root-owned directories)"
                exit 1
            fi
        else
            echo "  ✓ Ownership correct"
        fi
    else
        echo "✓ Creating: $dir"
        mkdir -p "$dir"
        chown "$USER_ID:$GROUP_ID" "$dir"
    fi
done

echo ""
echo "Creating .gitkeep files to maintain directory structure..."

# Create .gitkeep files
GITKEEP_DIRS=(
    "webadmin/email_templates_imported"
    "webadmin/dns_zones"
)

for dir in "${GITKEEP_DIRS[@]}"; do
    if [ ! -f "$dir/.gitkeep" ]; then
        echo "✓ Creating $dir/.gitkeep"
        touch "$dir/.gitkeep"
        chown "$USER_ID:$GROUP_ID" "$dir/.gitkeep"
    else
        echo "✓ Exists: $dir/.gitkeep"
    fi
done

echo ""
echo "Setting proper permissions..."

# Set directory permissions (755 = rwxr-xr-x)
find webadmin/email_templates_imported webadmin/dns_zones templates -type d -exec chmod 755 {} \; 2>/dev/null || true

# Set file permissions (644 = rw-r--r--)
find webadmin/email_templates_imported webadmin/dns_zones -type f -exec chmod 644 {} \; 2>/dev/null || true

echo ""
echo "✅ Directory structure initialized successfully!"
echo ""
echo "Summary:"
echo "  • All directories created with user ownership ($USER_ID:$GROUP_ID)"
echo "  • .gitkeep files added to maintain structure in git"
echo "  • Permissions set correctly (dirs: 755, files: 644)"
echo ""
echo "You can now run:"
echo "  ./docker_phishly-deploy.sh  (Docker)"
echo "  ./podman_phishly-deploy.sh  (Podman)"
echo ""
