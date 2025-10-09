"""
User management API endpoints.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import (
    get_admin_user,
    get_current_active_user,
    get_db,
    get_user_service,
)
from models.user import User, UserRole
from schemas.user import UserList, UserPublic, UserUpdate
from services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile."""
    return UserPublic.model_validate(current_user)


@router.put("/me", response_model=UserPublic)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update current user's profile."""

    try:
        # Users can only update their email, not role
        update_data = UserUpdate(email=user_data.email)

        updated_user = await user_service.update_user(current_user.id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserPublic.model_validate(updated_user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=UserList)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    current_user: User = Depends(get_admin_user),  # Only admins can list users
    user_service: UserService = Depends(get_user_service)
):
    """Get paginated list of users (admin only)."""

    skip = (page - 1) * size
    users, total = await user_service.list_users(
        skip=skip,
        limit=size,
        role_filter=role
    )

    return UserList(
        users=[UserPublic.model_validate(user) for user in users],
        total=total,
        page=page,
        size=size
    )


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_admin_user),  # Only admins can view any user
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID (admin only)."""

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserPublic.model_validate(user)


@router.put("/{user_id}", response_model=UserPublic)
async def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_admin_user),  # Only admins can update any user
    user_service: UserService = Depends(get_user_service)
):
    """Update user by ID (admin only)."""

    try:
        updated_user = await user_service.update_user(user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserPublic.model_validate(updated_user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: int,
    current_user: User = Depends(get_admin_user),  # Only admins can delete users
    user_service: UserService = Depends(get_user_service)
):
    """Delete user by ID (admin only)."""

    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return None


@router.get("/{user_id}/products", dependencies=[Depends(get_admin_user)])
async def get_user_products(user_id: int):
    """Get products owned by a specific user (admin only)."""
    # This endpoint will be implemented when we create product management
    return {"message": f"Products for user {user_id} - to be implemented"}