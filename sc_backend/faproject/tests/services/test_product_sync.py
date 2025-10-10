from unittest.mock import AsyncMock

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from models.product import Product
from repositories.product import ProductRepository
from services.product_sync import ProductSyncService


@pytest.mark.asyncio
async def test_sync_products_with_real_dummyjson(monkeypatch):
    """
    Інтеграційний тест: тягне реальні продукти з dummyjson.com
    і перевіряє map_to_internal + sync.
    """
    from services.dummyjson_integrator import DummyJsonProductIntegrator

    integrator = DummyJsonProductIntegrator()
    # Мокаємо БД та репозиторій, але fetch_products реальний
    db = AsyncMock(spec=AsyncSession)
    repo = AsyncMock(spec=ProductRepository)
    system_owner_id = 42
    service = ProductSyncService(db, integrator, system_owner_id)
    service.repo = repo

    # Для всіх продуктів repo.get_by_external_id повертає None
    # (імітація нових продуктів)
    products_from_api = await integrator.fetch_products()
    repo.get_by_external_id.side_effect = [None] * len(products_from_api)

    def create_side_effect(product_in, owner_id):
        # Повертаємо Product з потрібними полями
        return Product(id=1, owner_id=owner_id, **product_in.model_dump())

    repo.create.side_effect = create_side_effect

    # Run
    products = await service.sync_products()
    assert len(products) == len(products_from_api)
    # Перевіряємо що хоча б один продукт має title, external_id, height
    found = False
    for ext, prod in zip(products_from_api, products):
        mapped = integrator.map_to_internal(ext)
        assert prod.title == mapped["title"]
        assert prod.owner_id == system_owner_id
        if mapped["height"] is not None:
            found = True
    assert found, "At least one product should have height from dimensions"
