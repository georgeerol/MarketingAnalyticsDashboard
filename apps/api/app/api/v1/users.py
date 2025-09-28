"""
User management API routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.services.interfaces import UserServiceProtocol
from app.api.deps import (
    get_user_service, 
    get_current_active_user_dep, 
    get_current_admin_user,
    get_pagination_params
)

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def get_users(
    pagination: dict = Depends(get_pagination_params),
    active_only: bool = Query(True, description="Filter active users only"),
    current_user = Depends(get_current_admin_user),
    user_service: UserServiceProtocol = Depends(get_user_service)
):
    """Get all users (admin only)"""
    users = user_service.get_users(
        skip=pagination["skip"],
        limit=pagination["limit"],
        active_only=active_only
    )
    
    total = user_service.get_users_count(active_only=active_only)
    
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=pagination["skip"] // pagination["limit"] + 1,
        per_page=pagination["limit"]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user = Depends(get_current_admin_user),
    user_service: UserServiceProtocol = Depends(get_user_service)
):
    """Get user by ID (admin only)"""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user = Depends(get_current_admin_user),
    user_service: UserServiceProtocol = Depends(get_user_service)
):
    """Update user (admin only)"""
    try:
        user = user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user = Depends(get_current_active_user_dep),
    user_service: UserServiceProtocol = Depends(get_user_service)
):
    """Update current user profile"""
    try:
        # Users can't change their own active status
        update_data = user_data.model_copy()
        update_data.is_active = None
        
        user = user_service.update_user(current_user.id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/deactivate", response_model=dict)
async def deactivate_user(
    user_id: int,
    current_user = Depends(get_current_admin_user),
    user_service: UserServiceProtocol = Depends(get_user_service)
):
    """Deactivate user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    success = user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}


@router.post("/{user_id}/activate", response_model=dict)
async def activate_user(
    user_id: int,
    current_user = Depends(get_current_admin_user),
    user_service: UserServiceProtocol = Depends(get_user_service)
):
    """Activate user (admin only)"""
    success = user_service.activate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User activated successfully"}
