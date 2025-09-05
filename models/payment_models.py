from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    enrollment_id: str
    amount: float
    payment_type: str
    payment_method: str
    payment_status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    due_date: datetime
    notes: Optional[str] = None
    payment_proof: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentProof(BaseModel):
    proof: str

class PaymentCreate(BaseModel):
    student_id: str
    enrollment_id: str
    amount: float
    payment_type: str
    payment_method: str
    due_date: datetime
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
