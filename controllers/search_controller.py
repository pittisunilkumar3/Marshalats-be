from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from utils.database import get_db
from utils.helpers import serialize_doc
from models.user_models import UserRole
import re

class SearchController:
    @staticmethod
    async def global_search(
        query: str,
        search_type: Optional[str] = None,
        limit: int = 50,
        current_user: dict = None
    ):
        """
        Perform global search across users, coaches, courses, and branches
        
        Args:
            query: Search term
            search_type: Optional filter for specific entity type (users, coaches, courses, branches)
            limit: Maximum results per category
            current_user: Current authenticated user
        """
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        db = get_db()
        results = {}
        
        # Create case-insensitive regex pattern
        search_pattern = {"$regex": re.escape(query.strip()), "$options": "i"}
        
        # Get current user role for access control
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                current_role = None
        
        # Search Users (Students, Coaches, etc.)
        if not search_type or search_type == "users":
            user_filter = {
                "$or": [
                    {"full_name": search_pattern},
                    {"email": search_pattern},
                    {"phone": search_pattern},
                    {"id": search_pattern}
                ]
            }
            
            # Apply role-based filtering
            if current_role == UserRole.COACH_ADMIN:
                if current_user.get("branch_id"):
                    user_filter["branch_id"] = current_user["branch_id"]
            elif current_role == UserRole.COACH:
                if current_user.get("branch_id"):
                    user_filter["branch_id"] = current_user["branch_id"]
                user_filter["role"] = UserRole.STUDENT.value
            
            users = await db.users.find(user_filter).limit(limit).to_list(length=limit)
            
            # Clean sensitive data
            for user in users:
                user.pop("password", None)
            
            results["users"] = {
                "data": serialize_doc(users),
                "count": len(users),
                "type": "users"
            }
        
        # Search Coaches
        if not search_type or search_type == "coaches":
            coach_filter = {
                "$or": [
                    {"full_name": search_pattern},
                    {"contact_info.email": search_pattern},
                    {"contact_info.phone": search_pattern},
                    {"id": search_pattern},
                    {"areas_of_expertise": search_pattern}
                ],
                "is_active": True
            }
            
            coaches = await db.coaches.find(coach_filter).limit(limit).to_list(length=limit)
            
            # Clean sensitive data
            for coach in coaches:
                if "contact_info" in coach and "password" in coach["contact_info"]:
                    coach["contact_info"].pop("password", None)
            
            results["coaches"] = {
                "data": serialize_doc(coaches),
                "count": len(coaches),
                "type": "coaches"
            }
        
        # Search Courses
        if not search_type or search_type == "courses":
            course_filter = {
                "$or": [
                    {"name": search_pattern},
                    {"description": search_pattern},
                    {"id": search_pattern},
                    {"difficulty_level": search_pattern}
                ],
                "settings.active": True
            }
            
            courses = await db.courses.find(course_filter).limit(limit).to_list(length=limit)
            
            results["courses"] = {
                "data": serialize_doc(courses),
                "count": len(courses),
                "type": "courses"
            }
        
        # Search Branches
        if not search_type or search_type == "branches":
            branch_filter = {
                "$or": [
                    {"branch.name": search_pattern},
                    {"branch.address.street": search_pattern},
                    {"branch.address.city": search_pattern},
                    {"branch.address.state": search_pattern},
                    {"id": search_pattern}
                ],
                "is_active": True
            }
            
            branches = await db.branches.find(branch_filter).limit(limit).to_list(length=limit)
            
            results["branches"] = {
                "data": serialize_doc(branches),
                "count": len(branches),
                "type": "branches"
            }
        
        # Calculate total results
        total_results = sum(category["count"] for category in results.values())
        
        return {
            "query": query,
            "total_results": total_results,
            "results": results,
            "message": f"Found {total_results} results for '{query}'"
        }
    
    @staticmethod
    async def search_users(
        query: str,
        role: Optional[UserRole] = None,
        branch_id: Optional[str] = None,
        limit: int = 50,
        current_user: dict = None
    ):
        """Search specifically in users with additional filters"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        db = get_db()
        
        # Create search pattern
        search_pattern = {"$regex": re.escape(query.strip()), "$options": "i"}
        
        # Build filter query
        filter_query = {
            "$or": [
                {"full_name": search_pattern},
                {"email": search_pattern},
                {"phone": search_pattern},
                {"id": search_pattern}
            ]
        }
        
        # Apply role filter
        if role:
            filter_query["role"] = role.value
        
        # Apply branch filter
        if branch_id:
            filter_query["branch_id"] = branch_id
        
        # Apply role-based access control
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                current_role = None
        
        if current_role == UserRole.COACH_ADMIN:
            if current_user.get("branch_id"):
                filter_query["branch_id"] = current_user["branch_id"]
        elif current_role == UserRole.COACH:
            if current_user.get("branch_id"):
                filter_query["branch_id"] = current_user["branch_id"]
            filter_query["role"] = UserRole.STUDENT.value
        
        users = await db.users.find(filter_query).limit(limit).to_list(length=limit)
        total_count = await db.users.count_documents(filter_query)
        
        # Clean sensitive data
        for user in users:
            user.pop("password", None)
        
        return {
            "query": query,
            "users": serialize_doc(users),
            "total": total_count,
            "count": len(users),
            "message": f"Found {len(users)} users matching '{query}'"
        }

    @staticmethod
    async def search_coaches(
        query: str,
        area_of_expertise: Optional[str] = None,
        active_only: bool = True,
        limit: int = 50,
        current_user: dict = None
    ):
        """Search specifically in coaches"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

        db = get_db()

        # Create search pattern
        search_pattern = {"$regex": re.escape(query.strip()), "$options": "i"}

        # Build filter query
        filter_query = {
            "$or": [
                {"full_name": search_pattern},
                {"contact_info.email": search_pattern},
                {"contact_info.phone": search_pattern},
                {"id": search_pattern},
                {"areas_of_expertise": search_pattern}
            ]
        }

        if active_only:
            filter_query["is_active"] = True

        if area_of_expertise:
            filter_query["areas_of_expertise"] = {"$in": [area_of_expertise]}

        coaches = await db.coaches.find(filter_query).limit(limit).to_list(length=limit)
        total_count = await db.coaches.count_documents(filter_query)

        # Clean sensitive data
        for coach in coaches:
            if "contact_info" in coach and "password" in coach["contact_info"]:
                coach["contact_info"].pop("password", None)

        return {
            "query": query,
            "coaches": serialize_doc(coaches),
            "total": total_count,
            "count": len(coaches),
            "message": f"Found {len(coaches)} coaches matching '{query}'"
        }

    @staticmethod
    async def search_courses(
        query: str,
        category_id: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        active_only: bool = True,
        limit: int = 50,
        current_user: dict = None
    ):
        """Search specifically in courses"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

        db = get_db()

        # Create search pattern
        search_pattern = {"$regex": re.escape(query.strip()), "$options": "i"}

        # Build filter query
        filter_query = {
            "$or": [
                {"name": search_pattern},
                {"description": search_pattern},
                {"id": search_pattern},
                {"difficulty_level": search_pattern}
            ]
        }

        if active_only:
            filter_query["settings.active"] = True

        if category_id:
            filter_query["category_id"] = category_id

        if difficulty_level:
            filter_query["difficulty_level"] = difficulty_level

        courses = await db.courses.find(filter_query).limit(limit).to_list(length=limit)
        total_count = await db.courses.count_documents(filter_query)

        return {
            "query": query,
            "courses": serialize_doc(courses),
            "total": total_count,
            "count": len(courses),
            "message": f"Found {len(courses)} courses matching '{query}'"
        }

    @staticmethod
    async def search_branches(
        query: str,
        active_only: bool = True,
        limit: int = 50,
        current_user: dict = None
    ):
        """Search specifically in branches"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

        db = get_db()

        # Create search pattern
        search_pattern = {"$regex": re.escape(query.strip()), "$options": "i"}

        # Build filter query
        filter_query = {
            "$or": [
                {"branch.name": search_pattern},
                {"branch.address.street": search_pattern},
                {"branch.address.city": search_pattern},
                {"branch.address.state": search_pattern},
                {"id": search_pattern}
            ]
        }

        if active_only:
            filter_query["is_active"] = True

        branches = await db.branches.find(filter_query).limit(limit).to_list(length=limit)
        total_count = await db.branches.count_documents(filter_query)

        return {
            "query": query,
            "branches": serialize_doc(branches),
            "total": total_count,
            "count": len(branches),
            "message": f"Found {len(branches)} branches matching '{query}'"
        }
