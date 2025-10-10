"""
Authentication and user schemas for request/response validation.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.user import UserRole


# Request schemas
class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "password": "securepassword123"}
        }
    )


class UserLoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "password": "securepassword123"}
        }
    )


# Response schemas
class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    role: UserRole = Field(..., description="User role")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"id": 1, "email": "user@example.com", "role": "user"}
        },
    )


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {"id": 1, "email": "user@example.com", "role": "user"},
            }
        }
    )


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password (min 8 characters)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newsecurepassword456",
            }
        }
    )


# JWT payload schema (internal use)
class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    exp: Optional[int] = Field(None, description="Expiration timestamp")
    iat: Optional[int] = Field(None, description="Issued at timestamp")
