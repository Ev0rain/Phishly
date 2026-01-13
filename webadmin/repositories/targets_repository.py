"""
Targets Repository - Real database implementation

Handles all target group and target-related database queries for the webadmin
"""

from repositories.base_repository import BaseRepository
from database import db
from db.models import TargetList, TargetListMember, Target, Department, AdminUser
from sqlalchemy import func
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TargetsRepository(BaseRepository):
    """Real database repository for target groups and targets"""

    @staticmethod
    def get_all_groups():
        """Return all target groups/lists with member counts"""
        try:
            # Query target lists with member count and creator name via join
            groups_query = (
                db.session.query(
                    TargetList.id,
                    TargetList.name,
                    TargetList.description,
                    TargetList.created_at,
                    TargetList.updated_at,
                    AdminUser.username.label("created_by"),
                    func.count(TargetListMember.id).label("target_count"),
                )
                .outerjoin(AdminUser, TargetList.created_by_id == AdminUser.id)
                .outerjoin(TargetListMember, TargetList.id == TargetListMember.target_list_id)
                .group_by(TargetList.id, AdminUser.username)
                .order_by(TargetList.created_at.desc())
                .all()
            )

            groups = []
            for group in groups_query:
                groups.append(
                    {
                        "id": group.id,
                        "name": group.name,
                        "description": group.description or "",
                        "target_count": group.target_count,
                        "created_at": group.created_at,
                        "updated_at": group.updated_at,
                        "created_by": group.created_by or "Unknown",
                    }
                )

            return groups

        except Exception as e:
            logger.error(f"Error getting all groups: {e}")
            return []

    @staticmethod
    def get_group_by_id(group_id):
        """Return a specific target group with full details"""
        try:
            target_list = db.session.query(TargetList).filter(TargetList.id == group_id).first()

            if not target_list:
                return None

            # Get member count
            member_count = (
                db.session.query(func.count(TargetListMember.id))
                .filter(TargetListMember.target_list_id == group_id)
                .scalar()
            )

            # Get creator name
            created_by = "Unknown"
            if target_list.created_by_id:
                admin = (
                    db.session.query(AdminUser)
                    .filter(AdminUser.id == target_list.created_by_id)
                    .first()
                )
                if admin:
                    created_by = admin.username

            # Get members
            members = TargetsRepository.get_group_members(group_id)

            return {
                "id": target_list.id,
                "name": target_list.name,
                "description": target_list.description or "",
                "target_count": member_count,
                "created_at": target_list.created_at,
                "updated_at": target_list.updated_at,
                "created_by": created_by,
                "members": members,
            }

        except Exception as e:
            logger.error(f"Error getting group by id {group_id}: {e}")
            return None

    @staticmethod
    def get_group_members(group_id):
        """Return members (targets) for a specific group"""
        try:
            # Join TargetListMember -> Target -> Department
            members_query = (
                db.session.query(
                    Target.id,
                    Target.email,
                    Target.first_name,
                    Target.last_name,
                    Target.position,
                    Department.name.label("department_name"),
                )
                .join(TargetListMember, Target.id == TargetListMember.target_id)
                .outerjoin(Department, Target.department_id == Department.id)
                .filter(TargetListMember.target_list_id == group_id)
                .all()
            )

            members = []
            for member in members_query:
                members.append(
                    {
                        "id": member.id,
                        "email": member.email,
                        "first_name": member.first_name or "",
                        "last_name": member.last_name or "",
                        "position": member.position or "",
                        "department": member.department_name or "Unknown",
                    }
                )

            return members

        except Exception as e:
            logger.error(f"Error getting group members for group {group_id}: {e}")
            return []

    @staticmethod
    def get_dashboard_stats():
        """Return statistics for dashboard display"""
        try:
            total_groups = db.session.query(func.count(TargetList.id)).scalar() or 0
            total_targets = db.session.query(func.count(Target.id)).scalar() or 0

            # Get most recent group
            most_recent = (
                db.session.query(TargetList).order_by(TargetList.created_at.desc()).first()
            )

            most_recent_group = None
            if most_recent:
                most_recent_group = {
                    "id": most_recent.id,
                    "name": most_recent.name,
                    "created_at": most_recent.created_at,
                }

            return {
                "total_groups": total_groups,
                "total_targets": total_targets,
                "most_recent_group": most_recent_group,
            }

        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {
                "total_groups": 0,
                "total_targets": 0,
                "most_recent_group": None,
            }

    @staticmethod
    def create_group(name, description, targets_list, created_by_id=None):
        """
        Create a new target group with targets

        Args:
            name: Group name
            description: Group description
            targets_list: List of target dictionaries with email, first_name, last_name, etc.
            created_by_id: ID of admin user creating the group (optional)

        Returns:
            dict: The newly created group or None if failed
        """
        try:
            # Create target list
            new_target_list = TargetList(
                name=name,
                description=description,
                created_by_id=created_by_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(new_target_list)
            db.session.flush()  # Get ID without committing

            # Process targets
            for target_data in targets_list:
                # Check if target exists by email
                existing_target = (
                    db.session.query(Target).filter(Target.email == target_data["email"]).first()
                )

                if existing_target:
                    target_id = existing_target.id
                else:
                    # Get or create department
                    dept_name = target_data.get("department", "").strip()
                    department_id = None

                    if dept_name:
                        dept = (
                            db.session.query(Department)
                            .filter(Department.name == dept_name)
                            .first()
                        )
                        if not dept:
                            dept = Department(name=dept_name)
                            db.session.add(dept)
                            db.session.flush()
                        department_id = dept.id

                    # Create new target
                    new_target = Target(
                        email=target_data["email"],
                        first_name=target_data.get("first_name", ""),
                        last_name=target_data.get("last_name", ""),
                        position=target_data.get("position", ""),
                        department_id=department_id,
                    )
                    db.session.add(new_target)
                    db.session.flush()
                    target_id = new_target.id

                # Add to target list
                membership = TargetListMember(
                    target_list_id=new_target_list.id, target_id=target_id
                )
                db.session.add(membership)

            # Commit all changes
            db.session.commit()

            return {
                "id": new_target_list.id,
                "name": new_target_list.name,
                "description": new_target_list.description,
                "target_count": len(targets_list),
                "created_at": new_target_list.created_at,
                "updated_at": new_target_list.updated_at,
                "created_by": "Admin User",
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating group: {e}")
            return None

    @staticmethod
    def parse_csv_targets(csv_content):
        """
        Parse CSV content into target list
        Expected CSV format: email,first_name,last_name,position,department

        Args:
            csv_content: String content of CSV file

        Returns:
            dict: Parsed targets with validation (targets, errors, count)
        """
        import csv
        from io import StringIO

        targets = []
        errors = []

        try:
            reader = csv.DictReader(StringIO(csv_content))

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                email = row.get("email", "").strip()

                if not email:
                    errors.append(f"Row {row_num}: Missing email address")
                    continue

                # Basic email validation
                if "@" not in email or "." not in email.split("@")[1]:
                    errors.append(f"Row {row_num}: Invalid email format - {email}")
                    continue

                target = {
                    "email": email,
                    "first_name": row.get("first_name", "").strip(),
                    "last_name": row.get("last_name", "").strip(),
                    "position": row.get("position", "").strip(),
                    "department": row.get("department", "").strip(),
                }

                targets.append(target)

        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")

        return {
            "targets": targets,
            "errors": errors,
            "count": len(targets),
        }
