"""
Global dependencies for the FastAPI application.
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session_maker
from models.user import User
from services.auth import verify_token
from services.user import UserService

# Security scheme for JWT authentication
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session dependency."""
    async with async_session_maker() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""

    # Verify token
    token_payload = verify_token(credentials.credentials)
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(int(token_payload.sub))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (placeholder for future user status checks)."""
    # In the future, you might add user.is_active check here
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role for access."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required.",
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for public endpoints)."""

    if not credentials:
        return None

    try:
        # Verify token
        token_payload = verify_token(credentials.credentials)
        if not token_payload:
            return None

        # Get user from database
        user_service = UserService(db)
        user = await user_service.get_user_by_id(int(token_payload.sub))
        return user

    except Exception:
        return None


# User service dependency
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get user service instance."""
    return UserService(db)
