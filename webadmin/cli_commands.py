"""
Flask CLI command to initialize database
"""
import click
from flask.cli import with_appcontext
from database import db
from db.models import AdminUser
from werkzeug.security import generate_password_hash
from datetime import datetime


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    try:
        db.create_all()
        click.echo("✅ Database tables created/verified.")
    except Exception as e:
        click.echo(f"⚠️  Error creating tables: {e}")
        db.session.rollback()

    # Check if admin exists
    try:
        admin = db.session.query(AdminUser).filter_by(username="admin").first()
    except Exception as e:
        click.echo(f"⚠️  Table may not exist, creating admin anyway: {e}")
        db.session.rollback()
        admin = None

    if not admin:
        # Create default admin
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

        click.echo("")
        click.echo("=" * 60)
        click.echo("📋 DEFAULT ADMIN CREATED:")
        click.echo("=" * 60)
        click.echo("  Username: admin")
        click.echo("  Password: admin123")
        click.echo("=" * 60)
        click.echo("⚠️  Please change the password after first login!")
    else:
        click.echo("Admin user already exists.")


def register_commands(app):
    """Register CLI commands with Flask app"""
    app.cli.add_command(init_db_command)
