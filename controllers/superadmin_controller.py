from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import os
from typing import Optional

from models.superadmin_models import SuperAdmin, SuperAdminRegister, SuperAdminLogin, SuperAdminResponse
from utils.database import get_db
from utils.helpers import serialize_doc

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "student_management_secret_key_2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class SuperAdminController:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def register_superadmin(admin_data: SuperAdminRegister):
        """Register a new super admin"""
        db = get_db()
        
        # Check if email already exists
        existing_admin = await db.superadmins.find_one({"email": admin_data.email})
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Hash password
        hashed_password = SuperAdminController.hash_password(admin_data.password)
        
        # Create super admin
        admin = SuperAdmin(
            full_name=admin_data.full_name,
            email=admin_data.email,
            phone=admin_data.phone,
            password_hash=hashed_password
        )
        
        # Save to database
        admin_dict = admin.dict()
        await db.superadmins.insert_one(admin_dict)
        
        # Return response without password hash
        admin_response = SuperAdminResponse(
            id=admin.id,
            full_name=admin.full_name,
            email=admin.email,
            phone=admin.phone,
            is_active=admin.is_active,
            created_at=admin.created_at,
            updated_at=admin.updated_at
        )
        
        return {
            "status": "success",
            "message": "Super admin registered successfully",
            "data": admin_response.dict()
        }

    @staticmethod
    async def login_superadmin(login_data: SuperAdminLogin):
        """Login super admin and return JWT token"""
        db = get_db()
        
        # Find super admin by email
        admin = await db.superadmins.find_one({"email": login_data.email})
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not SuperAdminController.verify_password(login_data.password, admin["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if admin is active
        if not admin.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Create access token
        access_token = SuperAdminController.create_access_token(
            data={"sub": admin["id"], "email": admin["email"], "role": "superadmin"}
        )
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "id": admin["id"],
                "full_name": admin["full_name"],
                "email": admin["email"],
                "phone": admin["phone"],
                "token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600  # seconds
            }
        }

    @staticmethod
    async def get_current_superadmin(token: str):
        """Get current super admin from token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            admin_id = payload.get("sub")
            if admin_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        db = get_db()
        admin = await db.superadmins.find_one({"id": admin_id})
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Super admin not found"
            )
        
        return serialize_doc(admin)
