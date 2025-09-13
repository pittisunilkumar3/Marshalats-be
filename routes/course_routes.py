from fastapi import APIRouter, Depends, Query
from typing import Optional
from controllers.course_controller import CourseController
from controllers.payment_controller import PaymentController
from models.course_models import CourseCreate, CourseUpdate
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.post("")
async def create_course(
    course_data: CourseCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    return await CourseController.create_course(course_data, current_user)

@router.get("")
async def get_courses(
    category_id: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    instructor_id: Optional[str] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    return await CourseController.get_courses(category_id, difficulty_level, instructor_id, active_only, skip, limit, current_user)

@router.get("/{course_id}")
async def get_course(
    course_id: str,
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    return await CourseController.get_course(course_id, current_user)

@router.put("/{course_id}")
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await CourseController.update_course(course_id, course_update, current_user)

@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Delete course - accessible by Super Admin only"""
    return await CourseController.delete_course(course_id, current_user)

@router.get("/{course_id}/stats")
async def get_course_stats(
    course_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await CourseController.get_course_stats(course_id, current_user)

@router.get("/{course_id}/payment-info")
async def get_course_payment_info(
    course_id: str,
    branch_id: str = Query(..., description="Branch ID"),
    duration: str = Query(..., description="Duration code")
):
    """Get payment information for a course (public endpoint for registration)"""
    return await PaymentController.get_course_payment_info(course_id, branch_id, duration)

@router.get("/public/all")
async def get_public_courses(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
):
    """Get all courses - Public endpoint (no authentication required)"""
    return await CourseController.get_public_courses(active_only, skip, limit)

@router.get("/public/by-category/{category_id}")
async def get_courses_by_category(
    category_id: str,
    difficulty_level: Optional[str] = None,
    active_only: bool = True,
    include_durations: bool = True,
    skip: int = 0,
    limit: int = 50
):
    """Get all courses filtered by category - Public endpoint (no authentication required)"""
    return await CourseController.get_courses_by_category(category_id, difficulty_level, active_only, include_durations, skip, limit)

@router.get("/public/by-location/{location_id}")
async def get_courses_by_location(
    location_id: str,
    category_id: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    include_durations: bool = True,
    include_branches: bool = False,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50
):
    """Get courses available at a specific location - Public endpoint (no authentication required)"""
    return await CourseController.get_courses_by_location(location_id, category_id, difficulty_level, include_durations, include_branches, active_only, skip, limit)
