"""
ProductSyncService: синхронізація продуктів із зовнішнього інтегратора у БД.
"""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models.product import Product
from repositories.product import ProductRepository
from schemas.product import ProductCreate
from services.external_integrator import ExternalProductIntegrator


class ProductSyncService:
    """Сервіс для синхронізації продуктів із зовнішнього інтегратора у БД."""

    def __init__(
        self,
        db: AsyncSession,
        integrator: ExternalProductIntegrator,
        system_owner_id: int,
    ):
        self.db = db
        self.integrator = integrator
        self.repo = ProductRepository(db)
        self.system_owner_id = system_owner_id

    async def sync_products(self) -> List[Product]:
        """
        Синхронізує продукти з інтегратора у БД:
        - Якщо external_id існує — оновлює продукт
        - Якщо не існує — створює новий продукт
        """
        external_products = await self.integrator.fetch_products()
        synced_products = []
        for ext in external_products:
            mapped = self.integrator.map_to_internal(ext)
            external_id = mapped["external_id"]
            existing = await self.repo.get_by_external_id(external_id)
            product_in = ProductCreate(
                **{k: v for k, v in mapped.items() if k != "external_id"}
            )
            if existing:
                # Оновлення
                for field, value in product_in.model_dump(exclude_unset=True).items():
                    setattr(existing, field, value)
                await self.db.commit()
                await self.db.refresh(existing)
                synced_products.append(existing)
            else:
                # Створення
                new_product = await self.repo.create(
                    product_in, owner_id=self.system_owner_id
                )
                # Оновити external_id (бо repo.create не приймає external_id)
                new_product.external_id = external_id
                await self.db.commit()
                await self.db.refresh(new_product)
                synced_products.append(new_product)
        return synced_products
