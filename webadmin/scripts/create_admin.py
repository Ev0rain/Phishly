#!/usr/bin/env python3
"""
Create Admin User Script

Interactive script to create a new admin user for Phishly webadmin.
Prompts for username, email, password, and full name.
"""

import sys
import os
import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db  # noqa: E402
from db.models import AdminUser  # noqa: E402
from auth_utils import create_admin_user  # noqa: E402
from app import create_app  # noqa: E402


def main():
    """Main function to create admin user"""
    print("\n" + "=" * 60)
    print("Phishly WebAdmin - Create Admin User")
    print("=" * 60 + "\n")

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Get user input
        print("Enter admin user details:\n")

        username = input("Username: ").strip()
        if not username:
            print("❌ Error: Username is required")
            return 1

        email = input("Email: ").strip()
        if not email or "@" not in email:
            print("❌ Error: Valid email is required")
            return 1

        full_name = input("Full Name (optional): ").strip() or None

        # Get password with confirmation
        password = getpass.getpass("Password: ")
        if not password:
            print("❌ Error: Password is required")
            return 1

        password_confirm = getpass.getpass("Confirm Password: ")
        if password != password_confirm:
            print("❌ Error: Passwords do not match")
            return 1

        # Check if user already exists
        existing = (
            db.session.query(AdminUser)
            .filter((AdminUser.username == username) | (AdminUser.email == email))
            .first()
        )

        if existing:
            if existing.username == username:
                print(f"❌ Error: Username '{username}' already exists")
            else:
                print(f"❌ Error: Email '{email}' already exists")
            return 1

        # Create admin user
        try:
            user = create_admin_user(
                username=username, email=email, password=password, full_name=full_name
            )

            if user:
                print("\n" + "=" * 60)
                print("✅ Admin user created successfully!")
                print("=" * 60)
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Full Name: {user.full_name or 'N/A'}")
                print(f"Created: {user.created_at}")
                print("=" * 60 + "\n")
                print("\nYou can now log in to the webadmin interface.")
                return 0
            else:
                print("❌ Error: Failed to create admin user")
                return 1

        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
