"""
User service for database operations.
"""

from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRole
from schemas.user import UserCreate, UserUpdate
from services.auth import hash_password


class UserService:
    """Service class for user-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Create user instance
        db_user = User(
            email=user_data.email, password=hashed_password, role=user_data.role
        )

        try:
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("User with this email already exists")

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Update fields if provided
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.role is not None:
            user.role = user_data.role

        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Email already in use")

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True

    async def list_users(
        self, skip: int = 0, limit: int = 10, role_filter: Optional[UserRole] = None
    ) -> tuple[List[User], int]:
        """Get paginated list of users."""
        # Build query
        query = select(User)

        if role_filter:
            query = query.where(User.role == role_filter)

        # Get total count
        count_query = select(func.count(User.id))
        if role_filter:
            count_query = count_query.where(User.role == role_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def change_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Change user password."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.password = hash_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def is_email_taken(
        self, email: str, exclude_user_id: Optional[int] = None
    ) -> bool:
        """Check if email is already taken by another user."""
        query = select(User).where(User.email == email)

        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
