from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from controllers.superadmin_controller import SuperAdminController
from models.superadmin_models import SuperAdminRegister, SuperAdminLogin

router = APIRouter()
security = HTTPBearer()

async def get_current_superadmin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current super admin from token"""
    return await SuperAdminController.get_current_superadmin(credentials.credentials)

@router.post("/register")
async def register_superadmin(admin_data: SuperAdminRegister):
    """Register a new super admin"""
    return await SuperAdminController.register_superadmin(admin_data)

@router.post("/login")
async def login_superadmin(login_data: SuperAdminLogin):
    """Login super admin and get JWT token"""
    return await SuperAdminController.login_superadmin(login_data)

@router.get("/me")
async def get_my_profile(current_admin = Depends(get_current_superadmin)):
    """Get current super admin profile"""
    # Remove password hash from response
    admin_data = {k: v for k, v in current_admin.items() if k != "password_hash"}
    return {
        "status": "success",
        "data": admin_data
    }

@router.get("/verify-token")
async def verify_token(current_admin = Depends(get_current_superadmin)):
    """Verify if token is valid"""
    return {
        "status": "success",
        "message": "Token is valid",
        "data": {
            "id": current_admin["id"],
            "email": current_admin["email"],
            "full_name": current_admin["full_name"]
        }
    }
