"""
Phishly WebAdmin - Authentication Utilities

This module provides authentication functionality using Flask-Login
and integrates with the AdminUser model for user management.
"""

from flask_login import LoginManager, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import logging

from database import db
from db.models import AdminUser

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login_page"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


# Make AdminUser compatible with Flask-Login
class AuthenticatedUser(UserMixin):
    """
    Wrapper class to make AdminUser compatible with Flask-Login.

    Flask-Login requires specific methods that don't exist on the SQLAlchemy model.
    This class wraps the AdminUser and provides those methods.
    """

    def __init__(self, admin_user):
        """
        Initialize authenticated user wrapper.

        Args:
            admin_user: AdminUser model instance to wrap
        """
        self.admin_user = admin_user
        self.id = admin_user.id
        self.username = admin_user.username
        self.email = admin_user.email
        self.full_name = admin_user.full_name
        self._is_active = admin_user.is_active

    def get_id(self):
        """Return user ID as string (required by Flask-Login)"""
        return str(self.id)

    @property
    def is_active(self):
        """Return True if user account is active"""
        return self._is_active

    @property
    def is_authenticated(self):
        """Return True if user is authenticated"""
        return True

    @property
    def is_anonymous(self):
        """Return False (we don't support anonymous users)"""
        return False

    def __repr__(self):
        """Return string representation of authenticated user."""
        return f"<AuthenticatedUser {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID for Flask-Login.

    This function is called by Flask-Login to reload the user object from the
    user ID stored in the session.

    Args:
        user_id: User ID as string

    Returns:
        AuthenticatedUser object or None if user not found
    """
    try:
        admin_user = db.session.get(AdminUser, int(user_id))
        if admin_user and admin_user.is_active:
            return AuthenticatedUser(admin_user)
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")

    return None


def authenticate_user(username, password):
    """
    Authenticate user credentials.

    Args:
        username: Username (unique)
        password: Plain text password to verify

    Returns:
        AuthenticatedUser object if successful, None otherwise
    """
    try:
        # Find user by username
        admin_user = db.session.query(AdminUser).filter_by(username=username).first()

        if not admin_user:
            logger.warning(f"Failed login attempt for non-existent user: {username}")
            return None

        if not admin_user.is_active:
            logger.warning(f"Failed login attempt for inactive user: {username}")
            return None

        # Verify password
        if not check_password_hash(admin_user.password_hash, password):
            logger.warning(f"Failed login attempt for user {username}: incorrect password")
            return None

        # Update last login timestamp
        admin_user.last_login = datetime.utcnow()
        db.session.commit()

        logger.info(f"Successful login for user: {username}")
        return AuthenticatedUser(admin_user)

    except Exception as e:
        logger.error(f"Error authenticating user {username}: {e}")
        db.session.rollback()
        return None


def create_admin_user(username, email, password, full_name=None):
    """
    Create new admin user.

    Args:
        username: Unique username
        email: Unique email address
        password: Plain text password (will be hashed)
        full_name: Optional full name

    Returns:
        Tuple of (AdminUser object, error_message)
        If successful: (user, None)
        If failed: (None, error_message)
    """
    try:
        # Validate uniqueness
        if db.session.query(AdminUser).filter_by(username=username).first():
            return None, "Username already exists"

        if db.session.query(AdminUser).filter_by(email=email).first():
            return None, "Email already exists"

        # Create user
        admin_user = AdminUser(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        db.session.add(admin_user)
        db.session.commit()

        logger.info(f"Created new admin user: {username} (ID: {admin_user.id})")
        return admin_user, None

    except Exception as e:
        logger.error(f"Error creating admin user {username}: {e}")
        db.session.rollback()
        return None, f"Database error: {str(e)}"


def update_password(user_id, new_password):
    """
    Update user password.

    Args:
        user_id: User ID
        new_password: New plain text password (will be hashed)

    Returns:
        True if successful, False otherwise
    """
    try:
        admin_user = db.session.get(AdminUser, user_id)

        if not admin_user:
            logger.error(f"Cannot update password: User {user_id} not found")
            return False

        admin_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        logger.info(f"Password updated for user: {admin_user.username}")
        return True

    except Exception as e:
        logger.error(f"Error updating password for user {user_id}: {e}")
        db.session.rollback()
        return False


def deactivate_user(user_id):
    """
    Deactivate user account (soft delete).

    Args:
        user_id: User ID

    Returns:
        True if successful, False otherwise
    """
    try:
        admin_user = db.session.get(AdminUser, user_id)

        if not admin_user:
            logger.error(f"Cannot deactivate: User {user_id} not found")
            return False

        admin_user.is_active = False
        db.session.commit()

        logger.info(f"Deactivated user: {admin_user.username}")
        return True

    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {e}")
        db.session.rollback()
        return False


def reactivate_user(user_id):
    """
    Reactivate user account.

    Args:
        user_id: User ID

    Returns:
        True if successful, False otherwise
    """
    try:
        admin_user = db.session.get(AdminUser, user_id)

        if not admin_user:
            logger.error(f"Cannot reactivate: User {user_id} not found")
            return False

        admin_user.is_active = True
        db.session.commit()

        logger.info(f"Reactivated user: {admin_user.username}")
        return True

    except Exception as e:
        logger.error(f"Error reactivating user {user_id}: {e}")
        db.session.rollback()
        return False
