from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: Optional[str] = None
    level: Optional[str] = None
    duration_months: int
    base_fee: float
    branch_pricing: Dict[str, float] = {}
    coach_id: Optional[str] = None
    schedule: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseCreate(BaseModel):
    name: str
    description: str
    category: Optional[str] = None
    level: Optional[str] = None
    duration_months: int
    base_fee: float
    branch_pricing: Optional[Dict[str, float]] = {}
    coach_id: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = {}

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration_months: Optional[int] = None
    base_fee: Optional[float] = None
    branch_pricing: Optional[Dict[str, float]] = None
    coach_id: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
