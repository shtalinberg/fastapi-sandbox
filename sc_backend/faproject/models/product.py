"""
Product model for product management.
"""
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Product(Base):
    """Product model for managing products catalog."""

    __tablename__ = "products"

    # Basic product info
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False
    )

    # External integration
    external_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True
    )

    # Dimensions
    height: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=8, scale=2),
        nullable=True
    )
    length: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=8, scale=2),
        nullable=True
    )
    depth: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=8, scale=2),
        nullable=True
    )

    # User relationship (owner of the product)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="products"
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title='{self.title}', external_id='{self.external_id}')>"