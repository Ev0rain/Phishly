#!/usr/bin/env python3
"""
Simple database initialization script using SQL
"""

import sys
import os
import psycopg2
from werkzeug.security import generate_password_hash

# Database connection parameters
DB_HOST = os.environ.get("POSTGRES_HOST", "postgres-db")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "phishly")
DB_USER = os.environ.get("POSTGRES_USER", "phishly_admin")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")


def create_admin_users_table():
    """Create admin_users table if it doesn't exist"""
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

    cursor = conn.cursor()

    print("🔧 Creating admin_users table...")

    # Create table SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS admin_users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(200),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("✅ Table created successfully!")

    # Check if admin user exists
    cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'admin'")
    count = cursor.fetchone()[0]

    if count == 0:
        print("\n🔐 Creating initial admin user...")

        password_hash = generate_password_hash("admin123")

        insert_sql = """
        INSERT INTO admin_users (username, email, password_hash, full_name, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """

        cursor.execute(
            insert_sql,
            ("admin", "admin@phishly.local", password_hash, "System Administrator", True),
        )

        conn.commit()

        print("✅ Initial admin user created!")
        print("\n" + "=" * 60)
        print("📋 LOGIN CREDENTIALS:")
        print("=" * 60)
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email:    admin@phishly.local")
        print("=" * 60)
        print("\n⚠️  IMPORTANT: Please change the password after first login!")
        print("🌐 Login at: http://localhost:8006/login\n")
    else:
        print("\n✅ Admin user already exists")

        # List existing users
        cursor.execute("SELECT username, email, is_active FROM admin_users")
        users = cursor.fetchall()
        print("\n📋 Existing admin users:")
        for username, email, is_active in users:
            print(f"  - {username} ({email}) - Active: {is_active}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    try:
        create_admin_users_table()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
