"""
Authentication utilities for password hashing and JWT token management.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from core.config import settings
from schemas.auth import TokenPayload


class PasswordManager:
    """Utility class for password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain password."""
        # Truncate password to 72 bytes for bcrypt compatibility
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
class JWTManager:
    """Utility class for JWT token creation and validation."""

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        # Set expiration time
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        })

        # Create the token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayload]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            # Validate payload structure
            if payload.get("sub") is None:
                return None

            return TokenPayload(
                sub=payload.get("sub"),
                email=payload.get("email"),
                role=payload.get("role"),
                exp=payload.get("exp"),
                iat=payload.get("iat")
            )

        except jwt.PyJWTError:
            return None

    @staticmethod
    def get_token_expires_in() -> int:
        """Get token expiration time in seconds."""
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password."""
    return PasswordManager.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return PasswordManager.verify_password(plain_password, hashed_password)


def create_access_token(
    user_id: int,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create an access token for a user."""
    data = {
        "sub": str(user_id),
        "email": email,
        "role": role
    }
    return JWTManager.create_access_token(data, expires_delta)


def verify_token(token: str) -> Optional[TokenPayload]:
    """Verify a JWT token."""
    return JWTManager.verify_token(token)


def get_token_expires_in() -> int:
    """Get token expiration time in seconds."""
    return JWTManager.get_token_expires_in()