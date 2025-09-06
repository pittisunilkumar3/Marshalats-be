from fastapi import HTTPException, Depends
from typing import Optional
from datetime import datetime

from models.course_models import CourseCreate, CourseUpdate, Course
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.database import get_db
from utils.helpers import serialize_doc

class CourseController:
    @staticmethod
    async def create_course(
        course_data: CourseCreate,
        current_user: dict = None
    ):
        """Create new course with comprehensive nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        course = Course(**course_data.dict())

        # Store the course with nested structure exactly as provided
        course_dict = course.dict()

        await db.courses.insert_one(course_dict)
        return {"message": "Course created successfully", "course_id": course.id}

    @staticmethod
    async def get_courses(
        category_id: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        instructor_id: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50,
        current_user: dict = None
    ):
        """Get courses with nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        filter_query = {}
        
        if active_only:
            filter_query["settings.active"] = True
        if category_id:
            filter_query["category_id"] = category_id
        if difficulty_level:
            filter_query["difficulty_level"] = difficulty_level
        if instructor_id:
            filter_query["instructor_id"] = instructor_id

        courses = await db.courses.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        return {"courses": serialize_doc(courses)}

    @staticmethod
    async def get_course(
        course_id: str,
        current_user: dict = None
    ):
        """Get course by ID with nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        course = await db.courses.find_one({"id": course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return serialize_doc(course)

    @staticmethod
    async def update_course(
        course_id: str,
        course_update: CourseUpdate,
        current_user: dict = None
    ):
        """Update course with nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        
        # Check if course exists
        existing_course = await db.courses.find_one({"id": course_id})
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Coach Admin permission check
        if current_user["role"] == UserRole.COACH_ADMIN:
            # Check if user is the instructor of this course or can manage it
            if existing_course.get("instructor_id") != current_user["id"]:
                raise HTTPException(status_code=403, detail="You can only update courses where you are the instructor.")

        update_data = {k: v for k, v in course_update.dict(exclude_unset=True).items()}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

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
        current_user: dict = None
    ):
        """Get statistics for a specific course."""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        course = await db.courses.find_one({"id": course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        active_enrollments = await db.enrollments.count_documents({"course_id": course_id, "is_active": True})

        stats = {
            "course_details": serialize_doc(course),
            "active_enrollments": active_enrollments
        }
        return stats

    @staticmethod
    async def delete_course(
        course_id: str,
        current_user: dict = None
    ):
        """Delete course (soft delete by setting active to False)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Check if course exists
        existing_course = await db.courses.find_one({"id": course_id})
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Soft delete by setting settings.active to False
        result = await db.courses.update_one(
            {"id": course_id},
            {"$set": {"settings.active": False, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")

        return {"message": "Course deleted successfully"}
