"""
User-related schemas for API operations.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters)",
    )
    role: Optional[UserRole] = Field(
        default=UserRole.USER, description="User role (admin/user)"
    )


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = Field(None, description="New email address")
    role: Optional[UserRole] = Field(None, description="New user role")


class UserInDB(UserBase):
    """Schema for user data as stored in database."""

    id: int = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserPublic(UserBase):
    """Schema for public user information (safe for API responses)."""

    id: int = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    created_at: datetime = Field(..., description="Registration date")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "role": "user",
                "created_at": "2025-10-08T20:30:00Z",
            }
        },
    )


class UserList(BaseModel):
    """Schema for paginated user list response."""

    users: list[UserPublic] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": 1,
                        "email": "admin@example.com",
                        "role": "admin",
                        "created_at": "2025-10-08T20:30:00Z",
                    },
                    {
                        "id": 2,
                        "email": "user@example.com",
                        "role": "user",
                        "created_at": "2025-10-08T20:35:00Z",
                    },
                ],
                "total": 2,
                "page": 1,
                "size": 10,
            }
        }
    )
