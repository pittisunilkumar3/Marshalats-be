from fastapi import APIRouter, Depends, status
from controllers.branch_controller import BranchController
from models.branch_models import BranchCreate, BranchUpdate
from models.holiday_models import HolidayCreate
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.unified_auth import require_role_unified

router = APIRouter()

@router.post("")
async def create_branch(
    branch_data: BranchCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Create a new branch - accessible by Super Admin with superadmin or regular tokens"""
    return await BranchController.create_branch(branch_data, current_user)

@router.get("")
async def get_branches(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    return await BranchController.get_branches(skip, limit, current_user)

@router.get("/{branch_id}")
async def get_branch(
    branch_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    return await BranchController.get_branch(branch_id, current_user)

@router.put("/{branch_id}")
async def update_branch(
    branch_id: str,
    branch_update: BranchUpdate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update branch - accessible by Super Admin and Coach Admin with unified tokens"""
    return await BranchController.update_branch(branch_id, branch_update, current_user)

@router.post("/{branch_id}/holidays", status_code=status.HTTP_201_CREATED)
async def create_holiday(
    branch_id: str,
    holiday_data: HolidayCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Create holiday for branch - accessible by Super Admin and Coach Admin with unified tokens"""
    return await BranchController.create_holiday(branch_id, holiday_data, current_user)

@router.get("/{branch_id}/holidays")
async def get_holidays(
    branch_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    return await BranchController.get_holidays(branch_id, current_user)

@router.delete("/{branch_id}/holidays/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    branch_id: str,
    holiday_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Delete holiday from branch - accessible by Super Admin and Coach Admin with unified tokens"""
    return await BranchController.delete_holiday(branch_id, holiday_id, current_user)
