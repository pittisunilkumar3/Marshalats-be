from fastapi import APIRouter, Depends, status
from controllers.payment_controller import PaymentController
from models.student_models import StudentPaymentCreate
from models.user_models import UserRole
from utils.auth import require_role

router = APIRouter()

@router.post("/students/payments", status_code=status.HTTP_201_CREATED)
async def student_process_payment(
    payment_data: StudentPaymentCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    return await PaymentController.student_process_payment(payment_data, current_user)
