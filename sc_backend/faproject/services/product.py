"""
ProductService: business logic for product operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from models.product import Product
from models.user import User
from repositories.product import ProductRepository
from schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Async service layer for product business logic and access control."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)

    async def get_product(self, product_id: int) -> Optional[Product]:
        product = await self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def list_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return await self.repo.list(skip=skip, limit=limit)

    async def create_product(
        self, product_in: ProductCreate, current_user: User
    ) -> Product:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can create products",
            )
        return await self.repo.create(product_in, owner_id=current_user.id)

    async def update_product(
        self, product_id: int, product_in: ProductUpdate, current_user: User
    ) -> Product:
        product = await self.get_product(product_id)
        if not current_user.is_admin and product.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update product",
            )
        return await self.repo.update(product, product_in)

    async def delete_product(self, product_id: int, current_user: User) -> None:
        product = await self.get_product(product_id)
        if not current_user.is_admin and product.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete product",
            )
        await self.repo.delete(product)
