from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional
from enum import Enum
import uuid

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    COACH_ADMIN = "coach_admin"
    COACH = "coach"
    STUDENT = "student"

class BaseUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    phone: str
    full_name: str
    role: UserRole
    branch_id: Optional[str] = None
    biometric_id: Optional[str] = None
    is_active: bool = True
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    role: UserRole
    branch_id: Optional[str] = None
    biometric_id: Optional[str] = None
    password: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    branch_id: Optional[str] = None
    biometric_id: Optional[str] = None
    is_active: Optional[bool] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
