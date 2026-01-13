"""
Base Repository for Phishly WebAdmin

Provides common database operations for all repositories
"""

from abc import ABC
from database import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """
    Abstract base repository with common database operations.

    All repository classes should inherit from this base class to get
    standard CRUD operations and error handling.
    """

    @staticmethod
    def commit():
        """
        Commit current database transaction.

        Raises:
            SQLAlchemyError: If commit fails
        """
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database commit failed: {e}")
            raise

    @staticmethod
    def rollback():
        """Rollback current database transaction"""
        db.session.rollback()

    @staticmethod
    def add(entity):
        """
        Add entity to session (not committed yet).

        Args:
            entity: SQLAlchemy model instance to add
        """
        db.session.add(entity)

    @staticmethod
    def delete(entity):
        """
        Delete entity from database.

        Args:
            entity: SQLAlchemy model instance to delete
        """
        db.session.delete(entity)

    @staticmethod
    def add_and_commit(entity):
        """
        Add entity and commit in one call.

        Args:
            entity: SQLAlchemy model instance to add

        Returns:
            The added entity with ID populated

        Raises:
            SQLAlchemyError: If add/commit fails
        """
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database add_and_commit failed: {e}")
            raise

    @staticmethod
    def delete_and_commit(entity):
        """
        Delete entity and commit in one call.

        Args:
            entity: SQLAlchemy model instance to delete

        Raises:
            SQLAlchemyError: If delete/commit fails
        """
        try:
            db.session.delete(entity)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database delete_and_commit failed: {e}")
            raise

    @staticmethod
    def flush():
        """
        Flush pending changes to database (doesn't commit).

        Useful for getting IDs of newly created objects before committing.
        """
        db.session.flush()
