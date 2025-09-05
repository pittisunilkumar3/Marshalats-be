from pydantic import BaseModel
from datetime import datetime

class StudentEnrollmentCreate(BaseModel):
    course_id: str
    branch_id: str
    start_date: datetime

class StudentPaymentCreate(BaseModel):
    enrollment_id: str
    amount: float
    payment_method: str
    transaction_id: str = None
    notes: str = None
