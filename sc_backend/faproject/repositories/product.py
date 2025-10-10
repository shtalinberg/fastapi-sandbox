"""
Product repository: CRUD operations for Product model.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    """Async repository for Product model (CRUD operations)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(Product.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        result = await self.db.execute(select(Product).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, product_in: ProductCreate, owner_id: int) -> Product:
        product = Product(**product_in.model_dump(), owner_id=owner_id)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product: Product, product_in: ProductUpdate) -> Product:
        for field, value in product_in.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit()
