"""
User model for authentication and user management.
"""
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .product import Product


class UserRole(str, Enum):
    """User roles enumeration."""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    # Basic user info
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # Authentication
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Role
    role: Mapped[UserRole] = mapped_column(
        String(20),
        default=UserRole.USER,
        nullable=False
    )

    # Relationships
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    @property
    def role_value(self) -> str:
        """Get string value of user role."""
        return self.role.value if hasattr(self.role, 'value') else str(self.role)