from fastapi import HTTPException, Depends, status, Request
from typing import Optional
from datetime import datetime, timedelta
import secrets
import jwt
import os
import logging
import uuid

from models.user_models import UserCreate, UserLogin, ForgotPassword, ResetPassword, UserUpdate, BaseUser, UserRole
from utils.auth import hash_password, verify_password, create_access_token, get_current_active_user
from utils.database import get_db
from utils.helpers import serialize_doc, log_activity, send_sms

class AuthController:
    @staticmethod
    async def register_user(user_data: UserCreate, request: Request):
        """Register a new student (public endpoint)"""
        db = get_db()
        
        # Check if user exists
        existing_user = await db.users.find_one({
            "$or": [{"email": user_data.email}, {"phone": user_data.phone}]
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email or phone already exists")
        
        # Generate password if not provided
        if not user_data.password:
            user_data.password = secrets.token_urlsafe(8)
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user dictionary manually to ensure all fields are included
        user_dict = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "phone": user_data.phone,
            "full_name": user_data.full_name,
            "role": user_data.role.value,  # Convert enum to string
            "branch_id": user_data.branch_id,
            "biometric_id": user_data.biometric_id,
            "is_active": True,
            "date_of_birth": user_data.date_of_birth.isoformat() if user_data.date_of_birth else None,  # Convert date to string
            "gender": user_data.gender,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_dict)
        
        # Send credentials via SMS (mock)
        sms_message = (
            f"Your account has been created.\n"
            f"Email: {user_dict['email']}\n"
            f"Password: {user_data.password}\n"
            f"Date of Birth: {user_dict['date_of_birth']}\n"
            f"Gender: {user_dict['gender']}"
        )
        await send_sms(user_dict["phone"], sms_message)
        
        await log_activity(
            request=request,
            action="user_registration",
            user_id=user_dict["id"],
            user_name=user_dict["full_name"],
            details={"email": user_dict["email"], "role": user_dict["role"]}
        )

        return {"message": "User registered successfully", "user_id": user_dict["id"]}

    @staticmethod
    async def login(user_credentials: UserLogin, request: Request):
        """User login"""
        db = get_db()
        
        user = await db.users.find_one({"email": user_credentials.email})
        if not user or not verify_password(user_credentials.password, user["password"]):
            await log_activity(
                request=request,
                action="login_attempt",
                status="failure",
                details={"email": user_credentials.email, "reason": "Incorrect email or password"}
            )
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        if not user.get("is_active", False):
            await log_activity(
                request=request,
                action="login_attempt",
                status="failure",
                user_id=user["id"],
                user_name=user["full_name"],
                details={"email": user_credentials.email, "reason": "Account is deactivated"}
            )
            raise HTTPException(status_code=400, detail="Account is deactivated")
        
        access_token = create_access_token(data={"sub": user["id"]})

        await log_activity(
            request=request,
            action="login_success",
            user_id=user["id"],
            user_name=user["full_name"],
            details={"email": user["email"]}
        )

        return {"access_token": access_token, "token_type": "bearer", "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"],
            "date_of_birth": user.get("date_of_birth"),
            "gender": user.get("gender")
        }}

    @staticmethod
    async def forgot_password(forgot_password_data: ForgotPassword):
        """Initiate password reset process"""
        db = get_db()
        user = await db.users.find_one({"email": forgot_password_data.email})
        if not user:
            # Don't reveal that the user does not exist
            return {"message": "If an account with that email exists, a password reset link has been sent."}

        # Generate a short-lived token for password reset
        reset_token = create_access_token(
            data={"sub": user["id"], "scope": "password_reset"},
            expires_delta=timedelta(minutes=15)
        )

        # In a real application, you would email this token to the user
        # For this example, we'll just log it.
        logging.info(f"Password reset token for {user['email']}: {reset_token}")

        await send_sms(user["phone"], f"Your password reset token is: {reset_token}")

        response = {"message": "If an account with that email exists, a password reset link has been sent."}
        if os.environ.get("TESTING") == "True":
            response["reset_token"] = reset_token
        return response

    @staticmethod
    async def reset_password(reset_password_data: ResetPassword):
        """Reset password using a token"""
        try:
            payload = jwt.decode(
                reset_password_data.token,
                os.environ.get('SECRET_KEY', 'student_management_secret_key_2025'),
                algorithms=["HS256"]
            )
            if payload.get("scope") != "password_reset":
                raise HTTPException(status_code=401, detail="Invalid token scope")

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        new_hashed_password = hash_password(reset_password_data.new_password)
        db = get_db()
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {"password": new_hashed_password, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "Password has been reset successfully."}

    @staticmethod
    async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
        """Get current user information"""
        user_info = current_user.copy()
        user_info.pop("password", None)
        user_info["date_of_birth"] = current_user.get("date_of_birth")
        user_info["gender"] = current_user.get("gender")
        return user_info

    @staticmethod
    async def update_profile(user_update: UserUpdate, current_user: dict = Depends(get_current_active_user)):
        """Update user profile"""
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Ensure date_of_birth and gender are included in the update
        if user_update.date_of_birth:
            update_data["date_of_birth"] = user_update.date_of_birth
        if user_update.gender:
            update_data["gender"] = user_update.gender
        
        db = get_db()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
        return {"message": "Profile updated successfully"}
