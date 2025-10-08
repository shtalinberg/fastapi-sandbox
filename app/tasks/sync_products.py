import asyncio
import logging
import httpx
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud.product import create_or_update_external_product
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def sync_products_from_external_api():
    """Synchronize products from external API"""
    while True:
        try:
            logger.info("Starting product synchronization from external API...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.EXTERNAL_API_URL, timeout=30.0)
                response.raise_for_status()
                products = response.json()
            
            db: Session = SessionLocal()
            try:
                for product_data in products:
                    external_id = product_data.get("id")
                    product_info = {
                        "title": product_data.get("title"),
                        "price": product_data.get("price"),
                        "description": product_data.get("description"),
                        "category": product_data.get("category"),
                        "image": product_data.get("image")
                    }
                    create_or_update_external_product(db, external_id, product_info)
                
                logger.info(f"Successfully synchronized {len(products)} products")
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Error synchronizing products: {e}")
        
        await asyncio.sleep(settings.SYNC_INTERVAL_SECONDS)
