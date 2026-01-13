#!/bin/bash
# Initialize database and create admin user

echo "🔧 Creating admin_users table..."

# Get database credentials from environment
DB_USER=${POSTGRES_USER:-phishly_admin}
DB_NAME=${POSTGRES_DB:-phishly}

# Create table using docker exec
docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" << 'EOF'
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
EOF

if [ $? -eq 0 ]; then
    echo "✅ Table created successfully!"

    # Now create admin user using Python
    echo "🔐 Creating admin user..."
    docker exec phishly-webadmin python << 'PYEOF'
from app import create_app
from database import db
from db.models import AdminUser
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()
with app.app_context():
    # Check if admin exists
    try:
        admin = db.session.query(AdminUser).filter_by(username='admin').first()
        if not admin:
            admin = AdminUser(
                username='admin',
                email='admin@phishly.local',
                password_hash=generate_password_hash('admin123'),
                full_name='System Administrator',
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(admin)
            db.session.commit()
            print("\n" + "="*60)
            print("📋 ADMIN USER CREATED:")
            print("="*60)
            print("  Username: admin")
            print("  Password: admin123")
            print("="*60)
            print("⚠️  Change password after first login!")
            print(f"🌐 Login: http://localhost:8006/login")
        else:
            print("✅ Admin user already exists")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
PYEOF

else
    echo "❌ Failed to create table"
    exit 1
fi

