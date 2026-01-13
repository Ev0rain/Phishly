import psycopg2
from werkzeug.security import generate_password_hash
import os

# Database connection
conn = psycopg2.connect(
    host="postgres-db",
    port=5432,
    dbname=os.environ.get("POSTGRES_DB", "phishly"),
    user="postgres",  # Use superuser
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

cursor = conn.cursor()

print("🔧 Creating admin_users table...")

# Create table
cursor.execute(
    """
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
)
conn.commit()
print("✅ Table created!")

# Check if admin exists
cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'admin'")
count = cursor.fetchone()[0]

if count == 0:
    print("🔐 Creating admin user...")
    password_hash = generate_password_hash("admin123")

    cursor.execute(
        """
        INSERT INTO admin_users (username, email, password_hash, full_name, is_active)
        VALUES (%s, %s, %s, %s, %s)
    """,
        ("admin", "admin@phishly.local", password_hash, "System Administrator", True),
    )

    conn.commit()

    print("\n" + "=" * 60)
    print("📋 ADMIN USER CREATED:")
    print("=" * 60)
    print("  Username: admin")
    print("  Password: admin123")
    print("  Email:    admin@phishly.local")
    print("=" * 60)
    print("⚠️  IMPORTANT: Change password after first login!")
    print("🌐 Login at: http://localhost:8006/login\n")
else:
    print("✅ Admin user already exists")

cursor.close()
conn.close()
