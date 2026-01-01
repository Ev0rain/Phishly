#!/usr/bin/env python3
"""
Redis Session Management Utilities for Phishly.

This script provides utilities for managing Flask sessions stored in Redis.
Sessions are stored in DB 0 with the following structure:

Session Key Format: session:<session_id>
Session Data Structure (Hash):
    - user_id: Admin user ID from database
    - role: User role (e.g., "admin")
    - created_at: ISO 8601 timestamp
    - last_activity: ISO 8601 timestamp
    - csrf_secret: CSRF token secret
    - ip_address: Client IP address
    - user_agent_hash: Hash of user agent string
    - mfa_verified: MFA verification status (0 or 1)

Default Session TTL: 1800 seconds (30 minutes)
"""

import redis
import sys
import json
from datetime import datetime
from typing import Optional, Dict, List


class SessionManager:
    """Manage Redis sessions for Phishly webadmin."""

    def __init__(self, host="localhost", port=6379, db=0):
        """
        Initialize Redis connection to session database.

        Args:
            host: Redis host (default: localhost)
            port: Redis port (default: 6379)
            db: Redis database number (default: 0 for sessions)
        """
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_ttl = 1800  # 30 minutes

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data by session ID.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary of session data or None if not found
        """
        key = f"session:{session_id}"
        session_data = self.redis.hgetall(key)

        if not session_data:
            return None

        # Get TTL
        ttl = self.redis.ttl(key)
        session_data["ttl"] = ttl
        session_data["session_id"] = session_id

        return session_data

    def list_sessions(self, pattern: str = "session:*") -> List[Dict]:
        """
        List all sessions matching pattern.

        Args:
            pattern: Redis key pattern (default: session:*)

        Returns:
            List of session dictionaries
        """
        sessions = []
        for key in self.redis.scan_iter(pattern):
            session_id = key.replace("session:", "")
            session = self.get_session(session_id)
            if session:
                sessions.append(session)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        key = f"session:{session_id}"
        result = self.redis.delete(key)
        return result > 0

    def extend_session(self, session_id: str, ttl: Optional[int] = None) -> bool:
        """
        Extend session TTL.

        Args:
            session_id: Session identifier
            ttl: New TTL in seconds (default: 1800)

        Returns:
            True if extended, False if session not found
        """
        key = f"session:{session_id}"
        if not self.redis.exists(key):
            return False

        ttl = ttl or self.default_ttl
        self.redis.expire(key, ttl)
        return True

    def get_user_sessions(self, user_id: int) -> List[Dict]:
        """
        Get all sessions for a specific user.

        Args:
            user_id: Admin user ID

        Returns:
            List of session dictionaries for this user
        """
        all_sessions = self.list_sessions()
        return [s for s in all_sessions if s.get("user_id") == str(user_id)]

    def cleanup_expired(self) -> int:
        """
        Clean up expired sessions (Redis handles this automatically).

        This method scans for sessions with TTL < 0.

        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for key in self.redis.scan_iter("session:*"):
            ttl = self.redis.ttl(key)
            if ttl < 0:  # No expiration set or expired
                self.redis.delete(key)
                count += 1
        return count

    def get_stats(self) -> Dict:
        """
        Get session statistics.

        Returns:
            Dictionary with session statistics
        """
        sessions = self.list_sessions()

        # Count active users
        active_users = set()
        for session in sessions:
            if session.get("user_id"):
                active_users.add(session["user_id"])

        return {
            "total_sessions": len(sessions),
            "active_users": len(active_users),
            "database": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }


def main():
    """CLI interface for session management."""
    import argparse

    parser = argparse.ArgumentParser(description="Phishly Redis Session Manager")
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List all sessions")
    list_parser.add_argument("--user-id", type=int, help="Filter by user ID")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get session details")
    get_parser.add_argument("session_id", help="Session ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a session")
    delete_parser.add_argument("session_id", help="Session ID")

    # Extend command
    extend_parser = subparsers.add_parser("extend", help="Extend session TTL")
    extend_parser.add_argument("session_id", help="Session ID")
    extend_parser.add_argument("--ttl", type=int, default=1800, help="TTL in seconds")

    # Stats command
    subparsers.add_parser("stats", help="Show session statistics")

    # Cleanup command
    subparsers.add_parser("cleanup", help="Clean up expired sessions")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = SessionManager(host=args.host, port=args.port)

    try:
        if args.command == "list":
            if args.user_id:
                sessions = manager.get_user_sessions(args.user_id)
            else:
                sessions = manager.list_sessions()
            print(json.dumps(sessions, indent=2))

        elif args.command == "get":
            session = manager.get_session(args.session_id)
            if session:
                print(json.dumps(session, indent=2))
            else:
                print(f"Session not found: {args.session_id}", file=sys.stderr)
                sys.exit(1)

        elif args.command == "delete":
            if manager.delete_session(args.session_id):
                print(f"Deleted session: {args.session_id}")
            else:
                print(f"Session not found: {args.session_id}", file=sys.stderr)
                sys.exit(1)

        elif args.command == "extend":
            if manager.extend_session(args.session_id, args.ttl):
                print(f"Extended session {args.session_id} with TTL {args.ttl}s")
            else:
                print(f"Session not found: {args.session_id}", file=sys.stderr)
                sys.exit(1)

        elif args.command == "stats":
            stats = manager.get_stats()
            print(json.dumps(stats, indent=2))

        elif args.command == "cleanup":
            count = manager.cleanup_expired()
            print(f"Cleaned up {count} expired sessions")

    except redis.ConnectionError:
        print(f"Error: Could not connect to Redis at {args.host}:{args.port}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
