#!/usr/bin/env python3
    sys.exit(main())
if __name__ == "__main__":


            return 1
            print(f"❌ Error creating admin user: {e}")
        except Exception as e:

                return 1
                print("❌ Error: Failed to create admin user")
            else:
                return 0
                print("=" * 60 + "\n")
                print("\nYou can now log in to the webadmin interface.")
                print(f"Created: {user.created_at}")
                print(f"Full Name: {user.full_name or 'N/A'}")
                print(f"Email: {user.email}")
                print(f"Username: {user.username}")
                print("=" * 60)
                print("✅ Admin user created successfully!")
                print("\n" + "=" * 60)
            if user:

            )
                full_name=full_name
                password=password,
                email=email,
                username=username,
            user = create_admin_user(
        try:
        # Create admin user

            return 1
                print(f"❌ Error: Email '{email}' already exists")
            else:
                print(f"❌ Error: Username '{username}' already exists")
            if existing.username == username:
        if existing:

        ).first()
            (AdminUser.username == username) | (AdminUser.email == email)
        existing = db.session.query(AdminUser).filter(
        # Check if user already exists

            return 1
            print("❌ Error: Passwords do not match")
        if password != password_confirm:
        password_confirm = getpass.getpass("Confirm Password: ")

            return 1
            print("❌ Error: Password is required")
        if not password:
        password = getpass.getpass("Password: ")
        # Get password with confirmation

        full_name = input("Full Name (optional): ").strip() or None

            return 1
            print("❌ Error: Valid email is required")
        if not email or "@" not in email:
        email = input("Email: ").strip()

            return 1
            print("❌ Error: Username is required")
        if not username:
        username = input("Username: ").strip()

        print("Enter admin user details:\n")
        # Get user input
    with app.app_context():

    app = create_app()
    # Create Flask app context

    print("=" * 60 + "\n")
    print("Phishly WebAdmin - Create Admin User")
    print("\n" + "=" * 60)
    """Main function to create admin user"""
def main():


from app import create_app
from auth_utils import create_admin_user
from db.models import AdminUser
from database import db

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add parent directory to path

import getpass
import os
import sys

"""
Prompts for username, email, password, and full name.
Interactive script to create a new admin user for Phishly webadmin.

Create Admin User Script
"""

