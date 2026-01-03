"""
Mock repository for target group data
This returns hardcoded data until the database is ready
"""

from datetime import datetime, timedelta


class MockTargetsRepository:
    """Mock data access layer for target groups and individual targets"""

    @staticmethod
    def get_all_groups():
        """Return all target groups/lists"""
        return [
            {
                "id": 1,
                "name": "Engineering Team",
                "description": "All software engineers and developers",
                "target_count": 45,
                "created_at": datetime.now() - timedelta(days=30),
                "updated_at": datetime.now() - timedelta(days=5),
                "created_by": "Admin User",
            },
            {
                "id": 2,
                "name": "Finance Department",
                "description": "Accounting, billing, and finance staff",
                "target_count": 12,
                "created_at": datetime.now() - timedelta(days=60),
                "updated_at": datetime.now() - timedelta(days=15),
                "created_by": "Admin User",
            },
            {
                "id": 3,
                "name": "Executive Team",
                "description": "C-level executives and senior management",
                "target_count": 8,
                "created_at": datetime.now() - timedelta(days=90),
                "updated_at": datetime.now() - timedelta(days=45),
                "created_by": "Admin User",
            },
            {
                "id": 4,
                "name": "Sales Team",
                "description": "Sales representatives and account managers",
                "target_count": 25,
                "created_at": datetime.now() - timedelta(days=45),
                "updated_at": datetime.now() - timedelta(days=10),
                "created_by": "Admin User",
            },
            {
                "id": 5,
                "name": "Marketing Department",
                "description": "Marketing, PR, and communications staff",
                "target_count": 18,
                "created_at": datetime.now() - timedelta(days=20),
                "updated_at": datetime.now() - timedelta(days=3),
                "created_by": "Admin User",
            },
            {
                "id": 6,
                "name": "HR & Admin",
                "description": "Human resources and administrative personnel",
                "target_count": 10,
                "created_at": datetime.now() - timedelta(days=75),
                "updated_at": datetime.now() - timedelta(days=25),
                "created_by": "Admin User",
            },
            {
                "id": 7,
                "name": "Customer Support",
                "description": "Customer service and technical support",
                "target_count": 32,
                "created_at": datetime.now() - timedelta(days=15),
                "updated_at": datetime.now() - timedelta(days=2),
                "created_by": "Admin User",
            },
            {
                "id": 8,
                "name": "IT & Security",
                "description": "IT infrastructure and security teams",
                "target_count": 14,
                "created_at": datetime.now() - timedelta(days=50),
                "updated_at": datetime.now() - timedelta(days=8),
                "created_by": "Admin User",
            },
        ]

    @staticmethod
    def get_group_by_id(group_id):
        """Return a specific target group with full details"""
        groups = MockTargetsRepository.get_all_groups()
        for group in groups:
            if group["id"] == group_id:
                # Add members list for this group
                group["members"] = MockTargetsRepository.get_group_members(group_id)
                return group
        return None

    @staticmethod
    def get_group_members(group_id):
        """Return members (targets) for a specific group"""
        # Sample members for different groups
        members_data = {
            1: [  # Engineering Team
                {
                    "id": 1,
                    "email": "john.doe@company.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "position": "Senior Developer",
                    "department": "Engineering",
                },
                {
                    "id": 2,
                    "email": "jane.smith@company.com",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "position": "Full Stack Engineer",
                    "department": "Engineering",
                },
                {
                    "id": 3,
                    "email": "mike.johnson@company.com",
                    "first_name": "Mike",
                    "last_name": "Johnson",
                    "position": "DevOps Engineer",
                    "department": "Engineering",
                },
            ],
            2: [  # Finance Department
                {
                    "id": 10,
                    "email": "sarah.williams@company.com",
                    "first_name": "Sarah",
                    "last_name": "Williams",
                    "position": "CFO",
                    "department": "Finance",
                },
                {
                    "id": 11,
                    "email": "david.brown@company.com",
                    "first_name": "David",
                    "last_name": "Brown",
                    "position": "Accountant",
                    "department": "Finance",
                },
            ],
            3: [  # Executive Team
                {
                    "id": 20,
                    "email": "robert.ceo@company.com",
                    "first_name": "Robert",
                    "last_name": "Anderson",
                    "position": "CEO",
                    "department": "Executive",
                },
                {
                    "id": 21,
                    "email": "emily.cto@company.com",
                    "first_name": "Emily",
                    "last_name": "Martinez",
                    "position": "CTO",
                    "department": "Executive",
                },
            ],
        }

        # Return members for the requested group, or empty list if not found
        return members_data.get(group_id, [])

    @staticmethod
    def get_dashboard_stats():
        """Return statistics for dashboard display"""
        groups = MockTargetsRepository.get_all_groups()
        total_groups = len(groups)
        total_targets = sum(group["target_count"] for group in groups)

        return {
            "total_groups": total_groups,
            "total_targets": total_targets,
            "most_recent_group": groups[0] if groups else None,
        }

    @staticmethod
    def create_group(name, description, targets_list):
        """
        Mock method to create a new target group
        In production, this would insert into database

        Args:
            name: Group name
            description: Group description
            targets_list: List of email addresses or target dictionaries

        Returns:
            dict: The newly created group
        """
        new_id = max([g["id"] for g in MockTargetsRepository.get_all_groups()]) + 1

        new_group = {
            "id": new_id,
            "name": name,
            "description": description,
            "target_count": len(targets_list),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": "Admin User",
        }

        # In real implementation, save to database here
        # For now, just return the mock group
        return new_group

    @staticmethod
    def parse_csv_targets(csv_content):
        """
        Parse CSV content into target list
        Expected CSV format: email,first_name,last_name,position,department

        Args:
            csv_content: String content of CSV file

        Returns:
            list: Parsed targets with validation
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
