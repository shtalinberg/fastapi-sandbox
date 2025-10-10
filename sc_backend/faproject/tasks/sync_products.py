"""
Celery task for periodic product sync from external API.
"""

import asyncio

from core.celery_app import celery_app
from db.database import async_session_maker
from services.dummyjson_integrator import DummyJsonProductIntegrator
from services.product_sync import ProductSyncService

SYSTEM_OWNER_ID = 1  # ID користувача-системи (змінити за потреби)


@celery_app.task(bind=True, name="tasks.sync_products.sync_products_task")
def sync_products_task(self):
    """
    Celery task: синхронізує продукти з dummyjson.com у БД.
    """

    async def _run():
        async with async_session_maker() as session:
            integrator = DummyJsonProductIntegrator()
            service = ProductSyncService(session, integrator, SYSTEM_OWNER_ID)
            await service.sync_products()

    asyncio.run(_run())
