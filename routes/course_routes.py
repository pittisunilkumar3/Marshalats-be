from fastapi import APIRouter, Depends
from typing import Optional
from controllers.course_controller import CourseController
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
