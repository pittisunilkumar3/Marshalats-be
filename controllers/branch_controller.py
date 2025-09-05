from fastapi import HTTPException, Depends, status
from typing import Optional
from datetime import datetime

from models.branch_models import BranchCreate, BranchUpdate, Branch
from models.holiday_models import HolidayCreate, Holiday
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.database import db
from utils.helpers import serialize_doc

class BranchController:
    @staticmethod
    async def create_branch(
        branch_data: BranchCreate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
    ):
        """Create new branch"""
        branch = Branch(**branch_data.dict())
        await db.branches.insert_one(branch.dict())
        return {"message": "Branch created successfully", "branch_id": branch.id}

    @staticmethod
    async def get_branches(
        skip: int = 0,
        limit: int = 50,
        current_user: dict = Depends(get_current_active_user)
    ):
        """Get all branches"""
        branches = await db.branches.find({"is_active": True}).skip(skip).limit(limit).to_list(length=limit)
        return {"branches": serialize_doc(branches)}

    @staticmethod
    async def get_branch(
        branch_id: str,
        current_user: dict = Depends(get_current_active_user)
    ):
        """Get branch by ID"""
        branch = await db.branches.find_one({"id": branch_id})
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")
        return serialize_doc(branch)

    @staticmethod
    async def update_branch(
        branch_id: str,
        branch_update: BranchUpdate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Update branch"""
        # Coach Admin permission check
        if current_user["role"] == UserRole.COACH_ADMIN:
            if current_user.get("branch_id") != branch_id:
                raise HTTPException(status_code=403, detail="You can only update your own branch.")
            # Restrict fields a Coach Admin can update
            update_dict = branch_update.dict(exclude_unset=True)
            restricted_fields = ["manager_id", "is_active"]
            for field in restricted_fields:
                if field in update_dict:
                    raise HTTPException(status_code=403, detail=f"Coach Admins cannot update the '{field}' field.")

        update_data = {k: v for k, v in branch_update.dict(exclude_unset=True).items()}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.branches.update_one(
            {"id": branch_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Branch not found")
        
        return {"message": "Branch updated successfully"}

    @staticmethod
    async def create_holiday(
        branch_id: str,
        holiday_data: HolidayCreate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Create a new holiday for a branch."""
        if current_user["role"] == UserRole.COACH_ADMIN and current_user.get("branch_id") != branch_id:
            raise HTTPException(status_code=403, detail="You can only add holidays to your own branch.")

        holiday = Holiday(
            **holiday_data.dict(),
            branch_id=branch_id
        )
        # Convert date to datetime for MongoDB serialization
        holiday_dict = holiday.dict()
        holiday_dict["date"] = datetime.combine(holiday_dict["date"], datetime.min.time())

        await db.holidays.insert_one(holiday_dict)
        return holiday

    @staticmethod
    async def get_holidays(
        branch_id: str,
        current_user: dict = Depends(get_current_active_user)
    ):
        """Get all holidays for a specific branch."""
        holidays = await db.holidays.find({"branch_id": branch_id}).to_list(1000)
        return {"holidays": serialize_doc(holidays)}

    @staticmethod
    async def delete_holiday(
        branch_id: str,
        holiday_id: str,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Delete a holiday for a branch."""
        if current_user["role"] == UserRole.COACH_ADMIN and current_user.get("branch_id") != branch_id:
            raise HTTPException(status_code=403, detail="You can only delete holidays from your own branch.")

        result = await db.holidays.delete_one({"id": holiday_id, "branch_id": branch_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Holiday not found")
        return
