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

class CourseInfo(BaseModel):
    category_id: str
    course_id: str
    duration: str

class BranchInfo(BaseModel):
    location_id: str
    branch_id: str

class BaseUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    full_name: str  # Auto-generated from first_name + last_name
    role: UserRole
    biometric_id: Optional[str] = None
    is_active: bool = True
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    # Nested course and branch information
    course: Optional[CourseInfo] = None
    branch: Optional[BranchInfo] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    role: UserRole
    password: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    biometric_id: Optional[str] = None
    course: Optional[CourseInfo] = None
    branch: Optional[BranchInfo] = None

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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    branch_id: Optional[str] = None
    biometric_id: Optional[str] = None
    is_active: Optional[bool] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    # Nested course and branch information (preferred)
    course: Optional[CourseInfo] = None
    branch: Optional[BranchInfo] = None
    # Flat fields for backward compatibility
    course_category_id: Optional[str] = None
    course_id: Optional[str] = None
    course_duration: Optional[str] = None
    location_id: Optional[str] = None
