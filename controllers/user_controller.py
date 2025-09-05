from fastapi import HTTPException, Depends, Request
from typing import Optional
from datetime import datetime
import secrets

from models.user_models import UserCreate, UserUpdate, BaseUser, UserRole
from utils.auth import hash_password, require_role, get_current_active_user
from utils.database import db
from utils.helpers import serialize_doc, log_activity, send_sms, send_whatsapp

class UserController:
    @staticmethod
    async def create_user(
        user_data: UserCreate,
        request: Request,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Create new user (Super Admin or Coach Admin)"""
        # If a coach admin is creating a user, they must be in the same branch
        if current_user["role"] == UserRole.COACH_ADMIN:
            if not current_user.get("branch_id") or user_data.branch_id != current_user["branch_id"]:
                raise HTTPException(status_code=403, detail="Coach Admins can only create users for their own branch.")
            # Coach admins cannot create other admins
            if user_data.role in [UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]:
                raise HTTPException(status_code=403, detail="Coach Admins cannot create other admin users.")

        # Check if user exists
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

        await db.users.insert_one(user_dict)
        
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
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Get users with filtering"""
        filter_query = {}
        if role:
            filter_query["role"] = role.value
        if branch_id:
            filter_query["branch_id"] = branch_id
        
        users = await db.users.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        for user in users:
            user.pop("password", None)
            user["date_of_birth"] = user.get("date_of_birth")
            user["gender"] = user.get("gender")
        
        return {"users": serialize_doc(users), "total": len(users)}

    @staticmethod
    async def update_user(
        user_id: str,
        user_update: UserUpdate,
        request: Request,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Update user (Super Admin or Coach Admin)"""
        target_user = await db.users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        if current_user["role"] == UserRole.COACH_ADMIN:
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
        
        result = await db.users.update_one(
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
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Force a password reset for a user (Admins only)."""
        target_user = await db.users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check permissions
        if current_user["role"] == UserRole.COACH_ADMIN:
            if target_user.get("branch_id") != current_user.get("branch_id"):
                raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for users in their own branch.")
            if target_user.get("role") not in [UserRole.STUDENT.value, UserRole.COACH.value]:
                raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for Students and Coaches.")

        # Generate a new temporary password
        new_password = secrets.token_urlsafe(8)
        hashed_password = hash_password(new_password)

        # Update the user's password in the database
        await db.users.update_one(
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
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
    ):
        """Deactivate user (Super Admin only)"""
        result = await db.users.update_one(
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
