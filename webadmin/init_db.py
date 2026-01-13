#!/usr/bin/env python3
"""
Initialize Phishly database and create first admin user
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
# Import ALL models so they're registered with SQLAlchemy metadata
from db.models import (
    AdminUser, Department, Target, TargetList, TargetListMember,
    EmailTemplate, LandingPage, Campaign, CampaignTargetList, CampaignTarget,
    EmailJob, EventType, Event, FormTemplate, FormQuestion, FormSubmission, FormAnswer
)
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize database tables"""
    app = create_app()

    with app.app_context():
        print("🔧 Creating database tables...")
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"⚠️  Tables may already exist: {e}")

        # Check if admin user exists
        try:
            admin_count = db.session.query(AdminUser).count()
            print(f"📊 Current admin users: {admin_count}")
        except Exception as e:
            print(f"⚠️  Error counting users (tables may not exist yet), creating user anyway...")
            db.session.rollback()  # Roll back failed transaction
            admin_count = 0

        if admin_count == 0:
            print("\n🔐 Creating initial admin user...")

            # Create default admin user
            admin = AdminUser(
                username="admin",
                email="admin@phishly.local",
                password_hash=generate_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                created_at=datetime.utcnow()
            )

            db.session.add(admin)
            db.session.commit()

            print("✅ Initial admin user created!")
            print("\n" + "="*60)
            print("📋 LOGIN CREDENTIALS:")
            print("="*60)
            print(f"  Username: admin")
            print(f"  Password: admin123")
            print(f"  Email:    admin@phishly.local")
            print("="*60)
            print("\n⚠️  IMPORTANT: Please change the password after first login!")
            print(f"🌐 Login at: http://localhost:8006/login\n")
        else:
            print("\n✅ Admin users already exist in database")

            # List existing users
            users = db.session.query(AdminUser).all()
            print("\n📋 Existing admin users:")
            for user in users:
                print(f"  - {user.username} ({user.email}) - Active: {user.is_active}")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

