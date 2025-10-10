"""
Integrator for dummyjson.com products API.
"""

from typing import List, Dict, Any
import httpx
from .external_integrator import ExternalProductIntegrator

DUMMYJSON_URL = "https://dummyjson.com/products"


class DummyJsonProductIntegrator(ExternalProductIntegrator):
    """Інтегратор для отримання продуктів з dummyjson.com."""

    async def fetch_products(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(DUMMYJSON_URL)
            resp.raise_for_status()
            data = resp.json()
            return data.get("products", [])

    def map_to_internal(self, external_product: Dict[str, Any]) -> Dict[str, Any]:
        # Мапінг полів dummyjson → Product
        dimensions = external_product.get("dimensions", {})
        return {
            "title": external_product.get("title", ""),
            "description": external_product.get("description", ""),
            "price": external_product.get("price", 0),
            "external_id": str(external_product.get("id")),
            # Якщо є dimensions, беремо height/length/depth, інакше None
            "height": dimensions.get("height"),
            "length": dimensions.get("length"),
            "depth": dimensions.get("depth"),
            # owner_id буде встановлено у сервісі синхронізації (наприклад, system user)
        }
