from fastapi import APIRouter, Depends, Request
from typing import Optional
from controllers.user_controller import UserController
from models.user_models import UserCreate, UserUpdate, UserRole
from utils.auth import require_role

router = APIRouter()

@router.post("")
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await UserController.create_user(user_data, request, current_user)

@router.get("")
async def get_users(
    role: Optional[UserRole] = None,
    branch_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await UserController.get_users(role, branch_id, skip, limit, current_user)

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await UserController.update_user(user_id, user_update, request, current_user)

@router.post("/{user_id}/force-password-reset")
async def force_password_reset(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await UserController.force_password_reset(user_id, request, current_user)

@router.delete("/{user_id}")
async def deactivate_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    return await UserController.deactivate_user(user_id, request, current_user)
