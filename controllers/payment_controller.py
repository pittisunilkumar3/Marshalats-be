from fastapi import HTTPException, Depends, status
from datetime import datetime

from models.payment_models import PaymentStatus
from models.student_models import StudentPaymentCreate
from models.user_models import UserRole
from utils.auth import require_role
from utils.database import db
from utils.helpers import send_whatsapp

class PaymentController:
    @staticmethod
    async def student_process_payment(
        payment_data: StudentPaymentCreate,
        current_user: dict = Depends(require_role([UserRole.STUDENT]))
    ):
        """Allow a student to process a payment for their enrollment."""
        student_id = current_user["id"]

        # Validate enrollment and payment
        enrollment = await db.enrollments.find_one({"id": payment_data.enrollment_id, "student_id": student_id})
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found or does not belong to you.")

        # Find the pending payment for this enrollment
        # This assumes there's a specific pending payment the student is trying to clear
        # In a real system, you might have a more complex payment reconciliation logic
        pending_payment = await db.payments.find_one({
            "enrollment_id": payment_data.enrollment_id,
            "student_id": student_id,
            "payment_status": PaymentStatus.PENDING.value,
            "amount": payment_data.amount  # Ensure the amount matches
        })

        if not pending_payment:
            raise HTTPException(status_code=400, detail="No matching pending payment found for this enrollment and amount.")

        # Simulate payment gateway interaction (update payment status)
        update_data = {
            "payment_status": PaymentStatus.PAID,
            "payment_method": payment_data.payment_method,
            "transaction_id": payment_data.transaction_id,
            "payment_date": datetime.utcnow(),
            "notes": payment_data.notes,
            "updated_at": datetime.utcnow()
        }

        result = await db.payments.update_one(
            {"id": pending_payment["id"]},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update payment status.")

        # Update enrollment payment status if needed (e.g., if all payments are cleared)
        # This logic might need to be more sophisticated in a real app
        await db.enrollments.update_one(
            {"id": enrollment["id"]},
            {"$set": {"payment_status": PaymentStatus.PAID}}  # Simplified: mark enrollment paid if this payment clears it
        )

        # Send payment confirmation
        await send_whatsapp(current_user["phone"], f"Payment of ₹{payment_data.amount} received for enrollment {payment_data.enrollment_id}. Thank you!")

        return {"message": "Payment processed successfully", "payment_id": pending_payment["id"]}
