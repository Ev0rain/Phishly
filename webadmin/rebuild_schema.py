#!/usr/bin/env python3
"""
Rebuild Database Schema from SQLAlchemy Models

This script drops and recreates all tables based on the SQLAlchemy models in db/models.py.
Use this to sync the database with the current model definitions.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import db, init_event_types
from db.models import Base
from sqlalchemy import text

def rebuild_schema():
    """Drop all tables and recreate from models"""
    print("\n" + "=" * 80)
    print("REBUILDING DATABASE SCHEMA FROM SQLALCHEMY MODELS")
    print("=" * 80)
    print("\n⚠️  WARNING: This will drop all existing tables and data!")

    app = create_app()

    with app.app_context():
        try:
            # Drop all tables
            print("\n1. Dropping all tables...")
            Base.metadata.drop_all(db.engine)
            print("✅ All tables dropped")

            # Create all tables from models
            print("\n2. Creating tables from SQLAlchemy models...")
            Base.metadata.create_all(db.engine)
            print("✅ All tables created")

            # Initialize event types
            print("\n3. Initializing event types...")
            init_event_types()
            print("✅ Event types initialized")

            # Create initial admin user
            print("\n4. Creating initial admin user...")
            from db.models import AdminUser
            from werkzeug.security import generate_password_hash
            from datetime import datetime

            # Check if admin exists
            existing_admin = db.session.query(AdminUser).filter_by(username="admin").first()

            if not existing_admin:
                admin = AdminUser(
                    username="admin",
                    email="admin@phishly.local",
                    password_hash=generate_password_hash("admin123"),
                    full_name="System Administrator",
                    is_active=True,
                    created_at=datetime.utcnow(),
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created (username: admin, password: admin123)")
            else:
                print("✅ Admin user already exists")

            # Show table list
            print("\n5. Verifying tables...")
            result = db.session.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            ))
            tables = [row[0] for row in result]
            print(f"✅ Created {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")

            print("\n" + "=" * 80)
            print("✅ DATABASE SCHEMA REBUILT SUCCESSFULLY!")
            print("=" * 80)
            print("\nLogin credentials:")
            print("  Username: admin")
            print("  Password: admin123")
            print("\n⚠️  IMPORTANT: Change the password after first login!")
            print()

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(rebuild_schema())
