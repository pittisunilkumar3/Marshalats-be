from fastapi import HTTPException, Depends, Request
from typing import Optional, List
from datetime import datetime, date
import secrets
import uuid

from models.user_models import UserCreate, UserUpdate, BaseUser, UserRole
from utils.auth import hash_password, require_role, get_current_active_user
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin
from utils.database import get_db
from utils.helpers import serialize_doc, log_activity, send_sms, send_whatsapp

class UserController:
    @staticmethod
    async def create_user(
        user_data: UserCreate,
        request: Request,
        current_user: dict = None
    ):
        """Create new user (Super Admin or Coach Admin)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")
        
        # If a coach admin is creating a user, they must be in the same branch
        if current_role == UserRole.COACH_ADMIN:
            if not current_user.get("branch_id") or user_data.branch_id != current_user["branch_id"]:
                raise HTTPException(status_code=403, detail="Coach Admins can only create users for their own branch.")
            # Coach admins cannot create other admins
            if user_data.role in [UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]:
                raise HTTPException(status_code=403, detail="Coach Admins cannot create other admin users.")

        # Check if user exists
        db = get_db()
        existing_user = await db.users.find_one({
            "$or": [{"email": user_data.email}, {"phone": user_data.phone}]
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Generate password if not provided
        if not user_data.password:
            user_data.password = secrets.token_urlsafe(8)
        
        hashed_password = hash_password(user_data.password)
        user = BaseUser(**user_data.dict())
        user_dict = user.dict()
        user_dict["password"] = hashed_password
        
        # Ensure date_of_birth and gender are included in the user creation
        if user_data.date_of_birth:
            user_dict["date_of_birth"] = user_data.date_of_birth
        if user_data.gender:
            user_dict["gender"] = user_data.gender

        await get_db().users.insert_one(user_dict)
        
        # Send credentials
        await send_sms(user.phone, f"Account created. Email: {user.email}, Password: {user_data.password}")
        
        await log_activity(
            request=request,
            action="admin_create_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"created_user_id": user.id, "created_user_email": user.email, "role": user.role}
        )

        return {"message": "User created successfully", "user_id": user.id}

    @staticmethod
    async def get_users(
        role: Optional[UserRole] = None,
        branch_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        current_user: dict = None
    ):
        """Get users with filtering - accessible by Super Admin, Coach Admin, and Coach"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        filter_query = {}
        
        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")
        
        # Apply role-based filtering
        if current_role == UserRole.COACH_ADMIN:
            # Coach admins can only see users in their branch
            if current_user.get("branch_id"):
                filter_query["branch_id"] = current_user["branch_id"]
        elif current_role == UserRole.COACH:
            # Coaches can only see students in their branch
            if current_user.get("branch_id"):
                filter_query["branch_id"] = current_user["branch_id"]
            filter_query["role"] = UserRole.STUDENT.value  # Only show students to coaches
        
        # Apply additional filters
        if role:
            # Only allow if current user has permission to see this role
            if current_role == UserRole.COACH and role != UserRole.STUDENT:
                raise HTTPException(status_code=403, detail="Coaches can only view student users")
            filter_query["role"] = role.value
            
        if branch_id:
            # Ensure user can only filter by their own branch if not super admin
            if current_role in [UserRole.COACH_ADMIN, UserRole.COACH]:
                if current_user.get("branch_id") != branch_id:
                    raise HTTPException(status_code=403, detail="You can only view users from your own branch")
            filter_query["branch_id"] = branch_id
        
        db = get_db()
        users = await db.users.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        total_count = await db.users.count_documents(filter_query)
        
        for user in users:
            user.pop("password", None)
            user["date_of_birth"] = user.get("date_of_birth")
            user["gender"] = user.get("gender")
        
        return {
            "users": serialize_doc(users), 
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "message": f"Retrieved {len(users)} users"
        }

    @staticmethod
    async def update_user(
        user_id: str,
        user_update: UserUpdate,
        request: Request,
        current_user: dict = None
    ):
        """Update user (Super Admin or Coach Admin)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        target_user = await get_db().users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")

        if current_role == UserRole.COACH_ADMIN:
            # Coach Admins can only update students in their own branch
            if target_user["role"] != UserRole.STUDENT.value:
                raise HTTPException(status_code=403, detail="Coach Admins can only update student profiles.")
            if target_user.get("branch_id") != current_user.get("branch_id"):
                raise HTTPException(status_code=403, detail="Coach Admins can only update students in their own branch.")

        update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items()}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        # Ensure date_of_birth and gender are included in the update
        if user_update.date_of_birth:
            update_data["date_of_birth"] = user_update.date_of_birth
        if user_update.gender:
            update_data["gender"] = user_update.gender

        update_data["updated_at"] = datetime.utcnow()
        
        result = await get_db().users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            # This case should be rare due to the check above, but it's good practice
            raise HTTPException(status_code=404, detail="User not found")
        
        await log_activity(
            request=request,
            action="admin_update_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"updated_user_id": user_id, "update_data": user_update.dict(exclude_unset=True)}
        )

        return {"message": "User updated successfully"}

    @staticmethod
    async def force_password_reset(
        user_id: str,
        request: Request,
        current_user: dict = None
    ):
        """Force a password reset for a user (Admins only)."""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        target_user = await get_db().users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")

        # Check permissions
        if current_role == UserRole.COACH_ADMIN:
            if target_user.get("branch_id") != current_user.get("branch_id"):
                raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for users in their own branch.")
            if target_user.get("role") not in [UserRole.STUDENT.value, UserRole.COACH.value]:
                raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for Students and Coaches.")

        # Generate a new temporary password
        new_password = secrets.token_urlsafe(8)
        hashed_password = hash_password(new_password)

        # Update the user's password in the database
        await get_db().users.update_one(
            {"id": user_id},
            {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
        )

        # Log the activity
        await log_activity(
            request=request,
            action="admin_force_password_reset",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"reset_user_id": user_id, "reset_user_email": target_user["email"]}
        )

        # Send the new password to the user
        message = f"Your password has been reset by an administrator. Your new temporary password is: {new_password}"
        await send_sms(target_user["phone"], message)
        await send_whatsapp(target_user["phone"], message)

        return {"message": f"Password for user {target_user['full_name']} has been reset and sent to them."}

    @staticmethod
    async def deactivate_user(
        user_id: str,
        request: Request,
        current_user: dict = None
    ):
        """Deactivate user (Super Admin only)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        result = await get_db().users.update_one(
            {"id": user_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        await log_activity(
            request=request,
            action="admin_deactivate_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"deactivated_user_id": user_id}
        )

        return {"message": "User deactivated successfully"}

    @staticmethod
    async def delete_user(
        user_id: str,
        request: Request,
        current_user: dict = None
    ):
        """Permanently delete user (Super Admin only)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Check if user exists
        user = await get_db().users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Don't allow deletion of super admin users
        if user.get("role") == "super_admin":
            raise HTTPException(status_code=403, detail="Cannot delete super admin users")

        # Delete user from database
        result = await get_db().users.delete_one({"id": user_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        # Log the deletion activity
        await log_activity(
            request=request,
            action="admin_delete_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"deleted_user_id": user_id, "deleted_user_email": user.get("email", "N/A")}
        )

        return {"message": "User deleted successfully"}

    @staticmethod
    async def get_student_details(
        current_user: dict = Depends(get_current_user_or_superadmin)
    ):
        """Get detailed student information with course enrollment data (Authenticated endpoint)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Build query based on user role
        query = {"role": "student", "is_active": True}

        # Role-based access control
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")

        # Apply branch filtering for non-super-admin users
        if current_role != UserRole.SUPER_ADMIN:
            user_branch_id = current_user.get("branch_id")
            if not user_branch_id:
                raise HTTPException(status_code=403, detail="User not assigned to any branch")
            query["branch_id"] = user_branch_id

        # Get students
        students_cursor = db.users.find(query)
        students = await students_cursor.to_list(1000)

        if not students:
            return {
                "message": "No students found",
                "students": [],
                "total": 0
            }

        # Enrich student data with course and enrollment information
        enriched_students = []

        for student in students:
            student_id = student["id"]

            # Calculate age from date_of_birth
            age = None
            if student.get("date_of_birth"):
                if isinstance(student["date_of_birth"], str):
                    try:
                        birth_date = datetime.strptime(student["date_of_birth"], "%Y-%m-%d").date()
                    except ValueError:
                        birth_date = None
                elif isinstance(student["date_of_birth"], date):
                    birth_date = student["date_of_birth"]
                else:
                    birth_date = None

                if birth_date:
                    today = date.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            # Get enrollments for this student
            enrollments = await db.enrollments.find({"student_id": student_id, "is_active": True}).to_list(100)

            # Get course details for each enrollment
            courses_info = []
            for enrollment in enrollments:
                course = await db.courses.find_one({"id": enrollment["course_id"]})
                if course:
                    # Calculate duration from enrollment dates
                    duration_days = None
                    if enrollment.get("start_date") and enrollment.get("end_date"):
                        start_date = enrollment["start_date"]
                        end_date = enrollment["end_date"]
                        if isinstance(start_date, str):
                            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        if isinstance(end_date, str):
                            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        duration_days = (end_date - start_date).days

                    # Determine level from course difficulty
                    level = course.get("difficulty_level", "Beginner")

                    courses_info.append({
                        "course_name": course.get("title", "Unknown Course"),
                        "level": level,
                        "duration": f"{duration_days} days" if duration_days else "Not specified",
                        "enrollment_date": enrollment.get("enrollment_date"),
                        "payment_status": enrollment.get("payment_status", "pending")
                    })

            # Prepare student details response
            student_details = {
                "student_id": student_id,
                "student_name": student.get("full_name", f"{student.get('first_name', '')} {student.get('last_name', '')}").strip(),
                "gender": student.get("gender", "Not specified"),
                "age": age,
                "courses": courses_info,
                "email": student.get("email"),
                "phone": student.get("phone"),
                "action": "view_profile"  # Default action - can be customized based on requirements
            }

            enriched_students.append(student_details)

        return {
            "message": f"Retrieved {len(enriched_students)} student details successfully",
            "students": enriched_students,
            "total": len(enriched_students)
        }
