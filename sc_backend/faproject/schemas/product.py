"""
Product-related schemas for API operations.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    """Base schema for product (shared fields)."""

    title: str = Field(..., max_length=200, description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price")
    external_id: Optional[str] = Field(
        None, max_length=100, description="External API product ID"
    )
    height: Optional[Decimal] = Field(None, gt=0, description="Product height (cm)")
    length: Optional[Decimal] = Field(None, gt=0, description="Product length (cm)")
    depth: Optional[Decimal] = Field(None, gt=0, description="Product depth (cm)")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating product fields."""

    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None)
    price: Optional[Decimal] = Field(None, gt=0)
    external_id: Optional[str] = Field(None, max_length=100)
    height: Optional[Decimal] = Field(None, gt=0)
    length: Optional[Decimal] = Field(None, gt=0)
    depth: Optional[Decimal] = Field(None, gt=0)


class ProductInDB(ProductBase):
    """Schema for product as stored in DB."""

    id: int = Field(..., description="Product ID")
    owner_id: int = Field(..., description="Owner user ID")

    model_config = ConfigDict(from_attributes=True)


class ProductPublic(ProductInDB):
    """Schema for public product info (API response)."""

    pass
