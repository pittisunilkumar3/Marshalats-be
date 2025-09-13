from fastapi import HTTPException, Depends, status
from typing import Optional
from datetime import datetime

from models.branch_models import BranchCreate, BranchUpdate, Branch
from models.holiday_models import HolidayCreate, Holiday
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.database import get_db
from utils.helpers import serialize_doc

class BranchController:
    @staticmethod
    async def create_branch(
        branch_data: BranchCreate,
        current_user: dict = None
    ):
        """Create new branch with comprehensive nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        db = get_db()
        branch = Branch(**branch_data.dict())
        
        # Store the branch with nested structure exactly as provided
        branch_dict = branch.dict()
        
        await db.branches.insert_one(branch_dict)
        return {"message": "Branch created successfully", "branch_id": branch.id}

    @staticmethod
    async def get_branches(
        skip: int = 0,
        limit: int = 50,
        current_user: dict = None
    ):
        """Get all branches with nested structure and statistics"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        branches = await db.branches.find({"is_active": True}).skip(skip).limit(limit).to_list(length=limit)

        # Enhance branches with coach and student counts
        enhanced_branches = []
        for branch in branches:
            branch_id = branch["id"]

            # Count coaches assigned to this branch
            coach_count = await db.coaches.count_documents({
                "branch_id": branch_id,
                "is_active": True
            })

            # Also count coaches assigned as managers or branch admins (if they exist in users collection)
            # Count manager if assigned
            if branch.get("manager_id"):
                manager_exists = await db.users.count_documents({
                    "id": branch["manager_id"],
                    "role": {"$in": ["coach", "coach_admin"]},
                    "is_active": True
                })
                coach_count += manager_exists

            # Count branch admins (coaches assigned as admins)
            if branch.get("assignments", {}).get("branch_admins"):
                admin_coaches = await db.users.count_documents({
                    "id": {"$in": branch["assignments"]["branch_admins"]},
                    "role": {"$in": ["coach", "coach_admin"]},
                    "is_active": True
                })
                coach_count += admin_coaches

            # Count students - try multiple methods to find the correct field structure
            branch_id = branch["id"]
            student_count = 0

            # Method 1: Try flat branch_id field
            student_count = await db.users.count_documents({
                "role": "student",
                "branch_id": branch_id,
                "is_active": True
            })

            # Method 2: If no results, try nested branch.branch_id field
            if student_count == 0:
                student_count = await db.users.count_documents({
                    "role": "student",
                    "branch.branch_id": branch_id,
                    "is_active": True
                })

            # Method 3: If still no results, count unique students from enrollments
            if student_count == 0:
                pipeline = [
                    {"$match": {"branch_id": branch_id, "is_active": True}},
                    {"$group": {"_id": "$student_id"}},
                    {"$count": "unique_students"}
                ]
                unique_students = await db.enrollments.aggregate(pipeline).to_list(length=1)
                student_count = unique_students[0]["unique_students"] if unique_students else 0

            # Add statistics to branch data
            branch_with_stats = {
                **branch,
                "statistics": {
                    "coach_count": coach_count,
                    "student_count": student_count,
                    "course_count": len(branch.get("operational_details", {}).get("courses_offered", [])),
                    "active_courses": len(branch.get("assignments", {}).get("courses", []))
                }
            }
            enhanced_branches.append(branch_with_stats)

        return {"branches": serialize_doc(enhanced_branches)}

    @staticmethod
    async def get_branch(
        branch_id: str,
        current_user: dict = None
    ):
        """Get branch by ID with nested structure and statistics"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        branch = await db.branches.find_one({"id": branch_id})
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        # Count coaches assigned to this branch
        coach_count = await db.coaches.count_documents({
            "branch_id": branch_id,
            "is_active": True
        })

        # Also count coaches assigned as managers or branch admins (if they exist in users collection)
        # Count manager if assigned
        if branch.get("manager_id"):
            manager_exists = await db.users.count_documents({
                "id": branch["manager_id"],
                "role": {"$in": ["coach", "coach_admin"]},
                "is_active": True
            })
            coach_count += manager_exists

        # Count branch admins (coaches assigned as admins)
        if branch.get("assignments", {}).get("branch_admins"):
            admin_coaches = await db.users.count_documents({
                "id": {"$in": branch["assignments"]["branch_admins"]},
                "role": {"$in": ["coach", "coach_admin"]},
                "is_active": True
            })
            coach_count += admin_coaches

        # Count students - try multiple methods to find the correct field structure
        student_count = 0

        # Method 1: Try flat branch_id field
        student_count = await db.users.count_documents({
            "role": "student",
            "branch_id": branch_id,
            "is_active": True
        })

        # Method 2: If no results, try nested branch.branch_id field
        if student_count == 0:
            student_count = await db.users.count_documents({
                "role": "student",
                "branch.branch_id": branch_id,
                "is_active": True
            })

        # Method 3: If still no results, count unique students from enrollments
        if student_count == 0:
            pipeline = [
                {"$match": {"branch_id": branch_id, "is_active": True}},
                {"$group": {"_id": "$student_id"}},
                {"$count": "unique_students"}
            ]
            unique_students = await db.enrollments.aggregate(pipeline).to_list(length=1)
            student_count = unique_students[0]["unique_students"] if unique_students else 0

        # Add statistics to branch data
        branch_with_stats = {
            **branch,
            "statistics": {
                "coach_count": coach_count,
                "student_count": student_count,
                "course_count": len(branch.get("operational_details", {}).get("courses_offered", [])),
                "active_courses": len(branch.get("assignments", {}).get("courses", []))
            }
        }

        return serialize_doc(branch_with_stats)

    @staticmethod
    async def get_branch_stats(
        branch_id: str,
        current_user: dict = None
    ):
        """Get detailed statistics for a specific branch"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        branch = await db.branches.find_one({"id": branch_id})
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        # Count coaches assigned to this branch
        coach_count = 0
        coach_details = []

        # First, get coaches directly assigned to this branch from coaches collection
        branch_coaches = await db.coaches.find({
            "branch_id": branch_id,
            "is_active": True
        }).to_list(length=100)

        coach_count += len(branch_coaches)
        for coach in branch_coaches:
            coach_details.append({
                "id": coach["id"],
                "name": coach.get("full_name", "Unknown"),
                "role": "Coach",
                "email": coach.get("email", coach.get("contact_info", {}).get("email", ""))
            })

        # Count manager if assigned (from users collection)
        if branch.get("manager_id"):
            manager = await db.users.find_one({
                "id": branch["manager_id"],
                "role": {"$in": ["coach", "coach_admin"]},
                "is_active": True
            })
            if manager:
                coach_count += 1
                coach_details.append({
                    "id": manager["id"],
                    "name": manager.get("full_name", "Unknown"),
                    "role": "Manager",
                    "email": manager.get("email", manager.get("contact_info", {}).get("email", ""))
                })

        # Count branch admins (coaches assigned as admins from users collection)
        if branch.get("assignments", {}).get("branch_admins"):
            admin_coaches = await db.users.find({
                "id": {"$in": branch["assignments"]["branch_admins"]},
                "role": {"$in": ["coach", "coach_admin"]},
                "is_active": True
            }).to_list(length=100)

            coach_count += len(admin_coaches)
            for coach in admin_coaches:
                coach_details.append({
                    "id": coach["id"],
                    "name": coach.get("full_name", "Unknown"),
                    "role": "Branch Admin",
                    "email": coach.get("email", coach.get("contact_info", {}).get("email", ""))
                })

        # Count students - try multiple methods to find the correct field structure
        student_count = 0
        students = []

        # Method 1: Try flat branch_id field
        students = await db.users.find({
            "role": "student",
            "branch_id": branch_id,
            "is_active": True
        }).to_list(length=1000)

        # Method 2: If no results, try nested branch.branch_id field
        if not students:
            students = await db.users.find({
                "role": "student",
                "branch.branch_id": branch_id,
                "is_active": True
            }).to_list(length=1000)

        student_count = len(students)

        # Method 3: If still no results, get students from enrollments
        if student_count == 0:
            enrollments = await db.enrollments.find({
                "branch_id": branch_id,
                "is_active": True
            }).to_list(length=1000)

            # Get unique student IDs
            student_ids = list(set([e["student_id"] for e in enrollments]))
            if student_ids:
                students = await db.users.find({
                    "id": {"$in": student_ids},
                    "role": "student",
                    "is_active": True
                }).to_list(length=1000)
                student_count = len(students)

        # Get course statistics
        course_count = len(branch.get("operational_details", {}).get("courses_offered", []))
        active_courses = len(branch.get("assignments", {}).get("courses", []))

        # Get enrollment statistics
        total_enrollments = await db.enrollments.count_documents({
            "branch_id": branch_id,
            "is_active": True
        })

        return {
            "branch_id": branch_id,
            "branch_name": branch.get("branch", {}).get("name", "Unknown"),
            "statistics": {
                "coach_count": coach_count,
                "student_count": student_count,
                "course_count": course_count,
                "active_courses": active_courses,
                "total_enrollments": total_enrollments
            },
            "coach_details": coach_details,
            "student_details": [
                {
                    "id": student["id"],
                    "name": student.get("full_name", "Unknown"),
                    "email": student.get("email", student.get("contact_info", {}).get("email", "")),
                    "enrollment_date": student.get("created_at", "")
                } for student in students[:10]  # Limit to first 10 for performance
            ]
        }

    @staticmethod
    async def update_branch(
        branch_id: str,
        branch_update: BranchUpdate,
        current_user: dict = None
    ):
        """Update branch with nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        db = get_db()
        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")
        
        # Coach Admin permission check
        if current_role == UserRole.COACH_ADMIN:
            # For nested structure, check if user is admin of this branch
            existing_branch = await db.branches.find_one({"id": branch_id})
            if not existing_branch:
                raise HTTPException(status_code=404, detail="Branch not found")
            
            # Check if current user is in the branch_admins list
            branch_admins = existing_branch.get("assignments", {}).get("branch_admins", [])
            if current_user["id"] not in branch_admins:
                raise HTTPException(status_code=403, detail="You can only update branches where you are listed as an admin.")
            
            # Restrict fields a Coach Admin can update
            update_dict = branch_update.dict(exclude_unset=True)
            restricted_fields = ["manager_id", "is_active", "assignments", "bank_details"]
            for field in restricted_fields:
                if field in update_dict:
                    raise HTTPException(status_code=403, detail=f"Coach Admins cannot update the '{field}' field.")

        update_data = {k: v for k, v in branch_update.dict(exclude_unset=True).items()}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.branches.update_one(
            {"id": branch_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Branch not found")
        
        return {"message": "Branch updated successfully"}

    @staticmethod
    async def create_holiday(
        branch_id: str,
        holiday_data: HolidayCreate,
        current_user: dict = None
    ):
        """Create a new holiday for a branch."""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")
        
        db = get_db()
        if current_role == UserRole.COACH_ADMIN and current_user.get("branch_id") != branch_id:
            raise HTTPException(status_code=403, detail="You can only add holidays to your own branch.")

        holiday = Holiday(
            **holiday_data.dict(),
            branch_id=branch_id
        )
        # Convert date to datetime for MongoDB serialization
        holiday_dict = holiday.dict()
        holiday_dict["date"] = datetime.combine(holiday_dict["date"], datetime.min.time())

        await db.holidays.insert_one(holiday_dict)
        return holiday

    @staticmethod
    async def get_holidays(
        branch_id: str,
        current_user: dict = None
    ):
        """Get all holidays for a specific branch."""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        db = get_db()
        holidays = await db.holidays.find({"branch_id": branch_id}).to_list(1000)
        return {"holidays": serialize_doc(holidays)}

    @staticmethod
    async def delete_holiday(
        branch_id: str,
        holiday_id: str,
        current_user: dict = None
    ):
        """Delete a holiday for a branch."""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        db = get_db()
        if current_user["role"] == UserRole.COACH_ADMIN and current_user.get("branch_id") != branch_id:
            raise HTTPException(status_code=403, detail="You can only delete holidays from your own branch.")

        result = await db.holidays.delete_one({"id": holiday_id, "branch_id": branch_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Holiday not found")
        return

    @staticmethod
    async def delete_branch(
        branch_id: str,
        current_user: dict = None
    ):
        """Delete branch (soft delete by setting is_active to False)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Check if branch exists
        existing_branch = await db.branches.find_one({"id": branch_id})
        if not existing_branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        # Soft delete by setting is_active to False
        result = await db.branches.update_one(
            {"id": branch_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Branch not found")

        return {"message": "Branch deleted successfully"}
