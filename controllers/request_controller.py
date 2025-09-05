from fastapi import HTTPException, Depends, status
from typing import Optional
from datetime import datetime, timedelta

from models.transfer_models import TransferRequestCreate, TransferRequest, TransferRequestUpdate, TransferRequestStatus
from models.coursechange_models import CourseChangeRequestCreate, CourseChangeRequest, CourseChangeRequestUpdate, CourseChangeRequestStatus
from models.enrollment_models import Enrollment
from models.user_models import UserRole
from utils.auth import require_role
from utils.database import db
from utils.helpers import serialize_doc

class RequestController:
    @staticmethod
    async def create_transfer_request(
        request_data: TransferRequestCreate,
        current_user: dict = Depends(require_role([UserRole.STUDENT]))
    ):
        """Create a new transfer request."""
        if not current_user.get("branch_id"):
            raise HTTPException(status_code=400, detail="User is not currently assigned to a branch.")

        transfer_request = TransferRequest(
            student_id=current_user["id"],
            current_branch_id=current_user["branch_id"],
            **request_data.dict()
        )
        await db.transfer_requests.insert_one(transfer_request.dict())
        return transfer_request

    @staticmethod
    async def get_transfer_requests(
        status: Optional[TransferRequestStatus] = None,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Get a list of transfer requests."""
        filter_query = {}
        if status:
            filter_query["status"] = status.value

        if current_user["role"] == UserRole.COACH_ADMIN:
            # Coach admins can only see requests for their branch
            filter_query["current_branch_id"] = current_user.get("branch_id")

        requests = await db.transfer_requests.find(filter_query).to_list(1000)
        return {"requests": serialize_doc(requests)}

    @staticmethod
    async def update_transfer_request(
        request_id: str,
        update_data: TransferRequestUpdate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Update a transfer request (approve/reject)."""
        transfer_request = await db.transfer_requests.find_one({"id": request_id})
        if not transfer_request:
            raise HTTPException(status_code=404, detail="Transfer request not found")

        if current_user["role"] == UserRole.COACH_ADMIN:
            if transfer_request["current_branch_id"] != current_user.get("branch_id"):
                raise HTTPException(status_code=403, detail="You can only manage requests for your own branch.")

        updated_request = await db.transfer_requests.find_one_and_update(
            {"id": request_id},
            {"$set": {"status": update_data.status, "updated_at": datetime.utcnow()}},
            return_document=True
        )

        # If approved, update the student's branch
        if update_data.status == TransferRequestStatus.APPROVED:
            await db.users.update_one(
                {"id": transfer_request["student_id"]},
                {"$set": {"branch_id": transfer_request["new_branch_id"]}}
            )

        return {"message": "Transfer request updated successfully.", "request": serialize_doc(updated_request)}

    @staticmethod
    async def create_course_change_request(
        request_data: CourseChangeRequestCreate,
        current_user: dict = Depends(require_role([UserRole.STUDENT]))
    ):
        """Create a new course change request."""
        # Find the current enrollment to ensure it belongs to the student and is active
        current_enrollment = await db.enrollments.find_one({
            "id": request_data.current_enrollment_id,
            "student_id": current_user["id"],
            "is_active": True
        })
        if not current_enrollment:
            raise HTTPException(status_code=404, detail="Active enrollment not found.")

        # Check if the new course exists
        new_course = await db.courses.find_one({"id": request_data.new_course_id})
        if not new_course:
            raise HTTPException(status_code=404, detail="New course not found.")

        course_change_request = CourseChangeRequest(
            student_id=current_user["id"],
            branch_id=current_enrollment["branch_id"],
            **request_data.dict()
        )
        await db.course_change_requests.insert_one(course_change_request.dict())
        return course_change_request

    @staticmethod
    async def get_course_change_requests(
        status: Optional[CourseChangeRequestStatus] = None,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Get a list of course change requests."""
        filter_query = {}
        if status:
            filter_query["status"] = status.value

        if current_user["role"] == UserRole.COACH_ADMIN:
            filter_query["branch_id"] = current_user.get("branch_id")

        requests = await db.course_change_requests.find(filter_query).to_list(1000)
        return {"requests": serialize_doc(requests)}

    @staticmethod
    async def update_course_change_request(
        request_id: str,
        update_data: CourseChangeRequestUpdate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Update a course change request (approve/reject)."""
        change_request = await db.course_change_requests.find_one({"id": request_id})
        if not change_request:
            raise HTTPException(status_code=404, detail="Course change request not found")

        if current_user["role"] == UserRole.COACH_ADMIN:
            if change_request["branch_id"] != current_user.get("branch_id"):
                raise HTTPException(status_code=403, detail="You can only manage requests for your own branch.")

        updated_request = await db.course_change_requests.find_one_and_update(
            {"id": request_id},
            {"$set": {"status": update_data.status.value, "updated_at": datetime.utcnow()}},
            return_document=True
        )

        # If approved, perform the change
        if update_data.status == CourseChangeRequestStatus.APPROVED:
            # 1. Deactivate old enrollment
            await db.enrollments.update_one(
                {"id": change_request["current_enrollment_id"]},
                {"$set": {"is_active": False}}
            )

            # 2. Create new enrollment
            new_course = await db.courses.find_one({"id": change_request["new_course_id"]})
            if not new_course:
                # This should be rare, but handle it
                raise HTTPException(status_code=404, detail="New course not found during approval process.")

            # Determine fee for the new course
            fee_amount = new_course.get("base_fee")
            branch_pricing = new_course.get("branch_pricing", {})
            if change_request["branch_id"] in branch_pricing:
                fee_amount = branch_pricing[change_request["branch_id"]]

            # For simplicity, we'll start a new standard enrollment.
            # A real-world scenario might involve complex fee calculations.
            new_enrollment = Enrollment(
                student_id=change_request["student_id"],
                course_id=change_request["new_course_id"],
                branch_id=change_request["branch_id"],
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=new_course["duration_months"] * 30),
                fee_amount=fee_amount,
                admission_fee=0  # No new admission fee for a course change
            )
            await db.enrollments.insert_one(new_enrollment.dict())

        return {"message": "Course change request updated successfully.", "request": serialize_doc(updated_request)}
