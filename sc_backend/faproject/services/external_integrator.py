"""
Abstract interface for external product integrators.
"""

from typing import List, Dict, Any
from abc import ABC, abstractmethod


class ExternalProductIntegrator(ABC):
    """Інтерфейс для інтеграції з зовнішніми API продуктів."""

    @abstractmethod
    async def fetch_products(self) -> List[Dict[str, Any]]:
        """
        Отримати список продуктів із зовнішнього API у вигляді списку словників.
        Кожен словник — це дані одного продукту у форматі інтегратора.
        """
        pass

    @abstractmethod
    def map_to_internal(self, external_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Мапінг зовнішнього продукту у внутрішню структуру Product (dict для SQLAlchemy).
        """
        pass
