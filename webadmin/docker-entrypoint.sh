#!/bin/sh
# Docker entrypoint script
# Fixes volume permissions before dropping to app user

set -e

# Directories that need write access (mounted volumes)
WRITABLE_DIRS="/app/dns_zones /app/shared_cache /app/campaign_landing_pages"

# Target user (matches docker-compose user directive)
TARGET_UID="${PUID:-1000}"
TARGET_GID="${PGID:-1000}"

# Fix ownership of writable directories
for dir in $WRITABLE_DIRS; do
    if [ -d "$dir" ] || [ -L "$dir" ]; then
        # Check if directory exists and fix ownership
        current_uid=$(stat -c '%u' "$dir" 2>/dev/null || echo "unknown")
        if [ "$current_uid" != "$TARGET_UID" ]; then
            echo "Fixing ownership of $dir ($current_uid -> $TARGET_UID:$TARGET_GID)"
            chown -R "$TARGET_UID:$TARGET_GID" "$dir" 2>/dev/null || true
        fi
    else
        # Create directory if it doesn't exist
        echo "Creating directory $dir"
        mkdir -p "$dir"
        chown "$TARGET_UID:$TARGET_GID" "$dir"
    fi
done

# Drop to app user and execute the command
# If already running as the target user, just exec
if [ "$(id -u)" = "$TARGET_UID" ]; then
    exec "$@"
else
    # Use su-exec if available (Alpine), otherwise use su
    if command -v su-exec >/dev/null 2>&1; then
        exec su-exec "$TARGET_UID:$TARGET_GID" "$@"
    else
        # Fallback: use gosu if available
        if command -v gosu >/dev/null 2>&1; then
            exec gosu "$TARGET_UID:$TARGET_GID" "$@"
        else
            # Last resort: just exec (already handled above for matching UID)
            exec "$@"
        fi
    fi
fi
