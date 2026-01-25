#!/usr/bin/env python3
"""
Clear all Redis sessions - useful for fixing session corruption issues
"""

import os
import sys
import redis

# Get Redis URL from environment
redis_url = os.environ.get("REDIS_URL")

if not redis_url:
    print("❌ REDIS_URL not set in environment")
    print("   Export it first: export REDIS_URL='redis://localhost:6379/0'")
    sys.exit(1)

try:
    # Connect to Redis
    r = redis.from_url(redis_url, decode_responses=False)

    # Find all session keys
    session_keys = r.keys("phishly:session:*")

    if not session_keys:
        print("✅ No session keys found in Redis")
        sys.exit(0)

    # Delete all session keys
    deleted = r.delete(*session_keys)

    print(f"✅ Cleared {deleted} session keys from Redis")
    print("   Users will need to log in again")

except redis.ConnectionError:
    print(f"❌ Could not connect to Redis at: {redis_url}")
    print("   Make sure Redis is running")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
