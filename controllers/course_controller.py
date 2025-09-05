from fastapi import HTTPException, Depends
from typing import Optional
from datetime import datetime

from models.course_models import CourseCreate, CourseUpdate, Course
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.database import db
from utils.helpers import serialize_doc

class CourseController:
    @staticmethod
    async def create_course(
        course_data: CourseCreate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
    ):
        """Create new course"""
        course = Course(**course_data.dict())
        await db.courses.insert_one(course.dict())
        return {"message": "Course created successfully", "course_id": course.id}

    @staticmethod
    async def get_courses(
        branch_id: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        current_user: dict = Depends(get_current_active_user)
    ):
        """Get courses"""
        filter_query = {"is_active": True}
        
        if category:
            filter_query["category"] = category
        if level:
            filter_query["level"] = level

        courses = await db.courses.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        
        # Filter by branch pricing if branch_id provided
        if branch_id:
            courses = [c for c in courses if branch_id in c.get("branch_pricing", {})]
        
        return {"courses": serialize_doc(courses)}

    @staticmethod
    async def update_course(
        course_id: str,
        course_update: CourseUpdate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Update course"""
        update_data = {k: v for k, v in course_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.courses.update_one(
            {"id": course_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {"message": "Course updated successfully"}

    @staticmethod
    async def get_course_stats(
        course_id: str,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Get statistics for a specific course."""
        course = await db.courses.find_one({"id": course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        active_enrollments = await db.enrollments.count_documents({"course_id": course_id, "is_active": True})

        stats = {
            "course_details": serialize_doc(course),
            "active_enrollments": active_enrollments
        }
        return stats
