from fastapi import HTTPException, Depends, status
from typing import Optional
from datetime import datetime, timedelta

from models.enrollment_models import EnrollmentCreate, Enrollment, PaymentStatus
from models.payment_models import Payment
from models.student_models import StudentEnrollmentCreate
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.database import db
from utils.helpers import serialize_doc, send_whatsapp

class EnrollmentController:
    @staticmethod
    async def create_enrollment(
        enrollment_data: EnrollmentCreate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Create student enrollment"""
        # Validate student, course, and branch exist
        student = await db.users.find_one({"id": enrollment_data.student_id, "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        course = await db.courses.find_one({"id": enrollment_data.course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        branch = await db.branches.find_one({"id": enrollment_data.branch_id})
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")
        
        # Calculate end date
        end_date = enrollment_data.start_date + timedelta(days=course["duration_months"] * 30)
        
        enrollment = Enrollment(
            **enrollment_data.dict(),
            end_date=end_date,
            next_due_date=enrollment_data.start_date + timedelta(days=30)
        )
        
        await db.enrollments.insert_one(enrollment.dict())
        
        # Create initial payment records
        admission_payment = Payment(
            student_id=enrollment_data.student_id,
            enrollment_id=enrollment.id,
            amount=enrollment_data.admission_fee,
            payment_type="admission_fee",
            payment_method="pending",
            payment_status=PaymentStatus.PENDING,
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        
        course_payment = Payment(
            student_id=enrollment_data.student_id,
            enrollment_id=enrollment.id,
            amount=enrollment_data.fee_amount,
            payment_type="course_fee",
            payment_method="pending", 
            payment_status=PaymentStatus.PENDING,
            due_date=enrollment_data.start_date
        )
        
        await db.payments.insert_many([admission_payment.dict(), course_payment.dict()])
        
        # Send enrollment confirmation
        await send_whatsapp(student["phone"], f"Welcome! You're enrolled in {course['name']}. Start date: {enrollment_data.start_date.date()}")
        
        return {"message": "Enrollment created successfully", "enrollment_id": enrollment.id}

    @staticmethod
    async def get_enrollments(
        student_id: Optional[str] = None,
        course_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        current_user: dict = Depends(get_current_active_user)
    ):
        """Get enrollments with filtering"""
        filter_query = {}
        if student_id:
            filter_query["student_id"] = student_id
        if course_id:
            filter_query["course_id"] = course_id
        if branch_id:
            filter_query["branch_id"] = branch_id
        
        # Role-based filtering
        if current_user["role"] == "student":
            filter_query["student_id"] = current_user["id"]
        elif current_user["role"] == "coach_admin" and current_user.get("branch_id"):
            filter_query["branch_id"] = current_user["branch_id"]
        
        enrollments = await db.enrollments.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        return {"enrollments": serialize_doc(enrollments)}

    @staticmethod
    async def get_student_courses(
        student_id: str,
        current_user: dict = Depends(get_current_active_user)
    ):
        """Get student's enrolled courses"""
        # Check permission
        if current_user["role"] == "student" and current_user["id"] != student_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        enrollments = await db.enrollments.find({"student_id": student_id, "is_active": True}).to_list(length=100)
        
        # Enrich with course details
        course_ids = [e["course_id"] for e in enrollments]
        courses = await db.courses.find({"id": {"$in": course_ids}}).to_list(length=100)
        
        course_dict = {c["id"]: c for c in courses}
        
        result = []
        for enrollment in enrollments:
            course = course_dict.get(enrollment["course_id"])
            if course:
                result.append({
                    "enrollment": enrollment,
                    "course": course
                })
        
        return {"enrolled_courses": serialize_doc(result)}

    @staticmethod
    async def student_enroll_in_course(
        enrollment_data: StudentEnrollmentCreate,
        current_user: dict = Depends(require_role([UserRole.STUDENT]))
    ):
        """Allow a student to enroll themselves in a course."""
        student_id = current_user["id"]

        # Validate student, course, and branch exist
        student = await db.users.find_one({"id": student_id, "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        course = await db.courses.find_one({"id": enrollment_data.course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        branch = await db.branches.find_one({"id": enrollment_data.branch_id})
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        # Check if student is already enrolled in this course
        existing_enrollment = await db.enrollments.find_one({
            "student_id": student_id,
            "course_id": enrollment_data.course_id,
            "is_active": True
        })
        if existing_enrollment:
            raise HTTPException(status_code=400, detail="Student already enrolled in this course.")

        # Determine fee_amount based on branch pricing
        admission_fee = 500.0  # Fixed admission fee
        fee_amount = course["base_fee"]
        if enrollment_data.branch_id in course.get("branch_pricing", {}):
            fee_amount = course["branch_pricing"][enrollment_data.branch_id]

        # Calculate end date
        end_date = enrollment_data.start_date + timedelta(days=course["duration_months"] * 30)

        enrollment = Enrollment(
            student_id=student_id,
            course_id=enrollment_data.course_id,
            branch_id=enrollment_data.branch_id,
            start_date=enrollment_data.start_date,
            end_date=end_date,
            fee_amount=fee_amount,
            admission_fee=admission_fee,
            next_due_date=enrollment_data.start_date + timedelta(days=30)
        )

        await db.enrollments.insert_one(enrollment.dict())

        # Create initial payment records (pending)
        admission_payment = Payment(
            student_id=student_id,
            enrollment_id=enrollment.id,
            amount=admission_fee,
            payment_type="admission_fee",
            payment_method="pending",
            payment_status=PaymentStatus.PENDING,
            due_date=datetime.utcnow() + timedelta(days=7)
        )

        course_payment = Payment(
            student_id=student_id,
            enrollment_id=enrollment.id,
            amount=fee_amount,
            payment_type="course_fee",
            payment_method="pending",
            payment_status=PaymentStatus.PENDING,
            due_date=enrollment_data.start_date
        )

        await db.payments.insert_many([admission_payment.dict(), course_payment.dict()])

        # Send enrollment confirmation
        await send_whatsapp(student["phone"], f"Welcome! You're enrolled in {course['name']}. Start date: {enrollment_data.start_date.date()}")

        return {"message": "Enrollment created successfully", "enrollment_id": enrollment.id}
