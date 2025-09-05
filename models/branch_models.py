from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, Dict
import uuid

class Branch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str
    city: str
    state: str
    pincode: str
    phone: str
    email: EmailStr
    manager_id: Optional[str] = None
    is_active: bool = True
    business_hours: Dict[str, Dict[str, str]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BranchCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    pincode: str
    phone: str
    email: EmailStr
    manager_id: Optional[str] = None
    business_hours: Optional[Dict[str, Dict[str, str]]] = {}

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    manager_id: Optional[str] = None
    business_hours: Optional[Dict[str, Dict[str, str]]] = None
    is_active: Optional[bool] = None
