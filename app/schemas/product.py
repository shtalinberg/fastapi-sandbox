from pydantic import BaseModel, Field
from typing import Optional


class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None


class Product(ProductBase):
    id: int
    external_id: Optional[int] = None

    class Config:
        from_attributes = True
