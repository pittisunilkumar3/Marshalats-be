from fastapi import APIRouter, Depends
from typing import Optional
from controllers.course_controller import CourseController
from models.course_models import CourseCreate, CourseUpdate
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user

router = APIRouter()

@router.post("")
async def create_course(
    course_data: CourseCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    return await CourseController.create_course(course_data, current_user)

@router.get("")
async def get_courses(
    branch_id: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    return await CourseController.get_courses(branch_id, category, level, skip, limit, current_user)

@router.put("/{course_id}")
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await CourseController.update_course(course_id, course_update, current_user)

@router.get("/{course_id}/stats")
async def get_course_stats(
    course_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await CourseController.get_course_stats(course_id, current_user)
