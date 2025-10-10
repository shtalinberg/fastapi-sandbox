"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_active_user, get_db, security
from models.user import User
from schemas.auth import (
    PasswordChangeRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from schemas.user import UserCreate
from services.auth import create_access_token, get_token_expires_in, verify_password
from services.user import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""

    user_service = UserService(db)

    # Check if email already exists
    if await user_service.is_email_taken(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    try:
        # Create user
        user_create = UserCreate(email=user_data.email, password=user_data.password)
        new_user = await user_service.create_user(user_create)

        # Create access token
        access_token = create_access_token(
            user_id=new_user.id, email=new_user.email, role=new_user.role_value
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=get_token_expires_in(),
            user=UserResponse(id=new_user.id, email=new_user.email, role=new_user.role),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access token."""

    user_service = UserService(db)

    # Get user by email
    user = await user_service.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Create access token
    access_token = create_access_token(
        user_id=user.id, email=user.email, role=user.role_value
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=get_token_expires_in(),
        user=UserResponse(id=user.id, email=user.email, role=user.role),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id, email=current_user.email, role=current_user.role
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password."""

    # Verify current password
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Change password
    user_service = UserService(db)
    await user_service.change_password(current_user.id, password_data.new_password)

    return {"message": "Password changed successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token (re-issue token for current user)."""

    user_service = UserService(db)

    # Get current user from token
    from services.auth import verify_token

    token_payload = verify_token(credentials.credentials)

    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Get fresh user data
    user = await user_service.get_user_by_id(int(token_payload.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # Create new access token
    access_token = create_access_token(
        user_id=user.id, email=user.email, role=user.role_value
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=get_token_expires_in(),
        user=UserResponse(id=user.id, email=user.email, role=user.role),
    )
